import json
from spade.agent import Agent
from spade.behaviour import State
from spade.message import Message
from spade.template import Template
from processing.dbmanagerstrategy import DBManagerStrategy
from base.fsm import BaseFSM
from processing.dbconnfactory import DBConnFactory
import util.config as cfg
from util.logger import LoggerImpl


class InsertSensorValue(State):
    """
    Behavior where the agent actually stores the detections made by the SensorAgents of the network
    """
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            if self.agent.sensor_values.match(msg):
                body: dict = json.loads(str(msg.body))
                if self.agent.check_strategy.check_values(body):
                    if cfg.logging["enabled"]:
                        self.agent.log.log("Message received from " + str(msg.sender) + ": " + str(msg.body))
                    db_coll = cfg.collections["sensors_detections"]
                    res = self.agent.db_conn.insert_sensor_value(str(msg.sender), body, db_coll)
                    if body.get(cfg.trigger_events["event"]):
                        if cfg.logging["enabled"]:
                            self.agent.log.log("EVENT DETECTED -----> TO BE CHECKED")
                        self.set("_id_read", res.inserted_id)
                        self.set("agent_jid", str(msg.sender))
                        self.set_next_state("STATE_TWO")
                    else:
                        self.set_next_state("STATE_ONE")
                else:
                    self.set_next_state("STATE_ONE")
            elif self.agent.config_update.match(msg):
                if cfg.logging["enabled"]:
                    self.agent.log.log("Message received from " + str(msg.sender) + ": " + str(msg.body))

                self.agent.db_conn.insert_node_config(str(msg.sender), json.loads(str(msg.body)))
                self.set_next_state("STATE_ONE")
            else:
                self.set_next_state("STATE_ONE")
        else:
            self.set_next_state("STATE_ONE")


class InformTrigger(State):
    """
    Behavior where the agent informs the TriggerAgent agent when an interesting event is detected
    """
    async def run(self):
        msg = Message(to=cfg.jid["trigger_agent"])
        msg.set_metadata("performative", "inform")
        document: dict = {"_id_read": str(self.get("_id_read")), "agent_jid": self.get("agent_jid")}
        msg.body = json.dumps(document)
        if cfg.logging["enabled"]:
            self.agent.log.log("Message sent to trigger")
        await self.send(msg)
        self.set_next_state("STATE_ONE")


class DBManagerAgentBehav(BaseFSM):
    """
    General agent behavior
    """
    async def on_start(self):
        await super().on_start()
        self.add_state(name="STATE_ONE", state=InsertSensorValue(), initial=True)
        self.add_state(name="STATE_TWO", state=InformTrigger())

        self.add_transition(source="STATE_ONE", dest="STATE_ONE")
        self.add_transition(source="STATE_ONE", dest="STATE_TWO")
        self.add_transition(source="STATE_TWO", dest="STATE_ONE")


class DBManagerAgent(Agent):
    def __init__(self, agent_jid: str, password: str):
        """
        :param agent_jid: unique identifier of the agent
        :param password: string used for agent authentication on the xmpp server
        """

        super().__init__(agent_jid, password)
        self.db_conn = DBConnFactory().create_manager_db_connector()
        self.check_strategy: DBManagerStrategy
        self.log = LoggerImpl(str(self.jid))
        self.sensor_values = Template()
        self.config_update = Template()

    async def setup(self):
        self.sensor_values.set_metadata("performative", "inform")
        self.sensor_values.set_metadata("service", "detection")
        self.config_update.set_metadata("performative", "inform")
        self.config_update.set_metadata("service", "config")

        self.add_behaviour(DBManagerAgentBehav())
