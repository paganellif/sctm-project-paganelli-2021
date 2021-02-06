import json
from spade.agent import Agent
from spade.behaviour import State
from spade.message import Message
from spade.template import Template
import util.config as cfg
from WSN.nodemanagerstrategy import CheckConfigStrategy, GetConfigStrategy
from base.fsm import BaseFSM
import util.ledmanager as led
from util.logger import LoggerImpl


class MsgReceiver(State):
    async def run(self):
        """
        Behavior where the agent communicates with the other SensorAgents of the network
        and the FrontEndAgent agent and computes the information regarding the status of the node
        """

        msg = await self.receive(timeout=10)
        if msg:
            # received a state update from the sensor agent
            if self.agent.state_update.match(msg):
                if cfg.logging["enabled"]:
                    self.agent.log.log("Message received from " + str(msg.sender) + ": " + str(msg.body))
                previous_state = cfg.node["state"]
                cfg.node["state"] = msg.body
                self.agent.update_led_from_state()

                # insert a new config if the state is changed
                if cfg.node["state"] is not previous_state:
                    new_config = Message(to=cfg.jid["dbmanager_agent"])
                    new_config.set_metadata("service", "config")
                    new_config.set_metadata("performative", "inform")
                    new_config.body = json.dumps(self.agent.get_config_strategy.get_config())
                    await self.send(new_config)

            # received a config update from frontend agent
            elif self.agent.config_update(msg):
                if cfg.logging["enabled"]:
                    self.agent.log.log("Message received from " + str(msg.sender) + ": " + str(msg.body))

                tmp = cfg.node["state"]
                if tmp != "ALARM ON":
                    cfg.node["state"] = "CHECKING"
                    self.agent.update_led_from_state()

                if self.agent.check_config_strategy.check_config(json.loads(msg.body)):
                    new_config = Message(to=cfg.jid["dbmanager_agent"])
                    new_config.set_metadata("service", "config")
                    new_config.set_metadata("performative", "inform")
                    new_config.body = json.dumps(self.agent.config_to_json())
                    await self.send(new_config)

                if tmp != "ALARM ON":
                    cfg.node["state"] = "RUNNING"
                    self.agent.update_led_from_state()

        self.set_next_state("STATE_ONE")


class NodeManagerAgentBehav(BaseFSM):
    """
    General agent behavior
    """

    async def on_start(self):
        await super().on_start()
        self.add_state(name="STATE_ONE", state=MsgReceiver(), initial=True)
        self.add_transition(source="STATE_ONE", dest="STATE_ONE")

        new_config = Message(to=cfg.jid["dbmanager_agent"])
        new_config.set_metadata("service", "config")
        new_config.set_metadata("performative", "inform")
        new_config.body = json.dumps(self.agent.get_config_strategy.get_config())
        await self.send(new_config)


class NodeManagerAgent(Agent):
    def __init__(self, agent_jid: str, password: str):
        """
        :param agent_jid: unique identifier of the agent
        :param password: string used for agent authentication on the xmpp server
        """

        super().__init__(agent_jid, password)
        self.log = LoggerImpl(str(self.jid))
        self.state_request = Template()
        self.state_update = Template()
        self.config_update = Template()
        self.check_config_strategy: CheckConfigStrategy
        self.get_config_strategy: GetConfigStrategy
        cfg.node["state"] = "RUNNING"
        led.green_led_on()

    async def setup(self):
        self.add_behaviour(NodeManagerAgentBehav())
        self.state_request.set_metadata("performative", "request")
        self.state_request.sender = cfg.jid["frontend_agent"]
        self.state_update.set_metadata("performative", "inform")
        self.state_update.sender = cfg.jid["sensor_agent"]
        self.config_update.set_metadata("performative", "inform")
        self.config_update.sender = cfg.jid["frontend_agent"]

    def update_led_from_state(self):
        if cfg.node["state"] == "RUNNING":
            led.green_led_on()
        elif cfg.node["state"] == "CHECKING":
            led.yellow_led_on()
        elif cfg.node["state"] == "ALARM ON":
            led.red_led_on()
