from spade.agent import Agent
from spade.template import Template
from spade.message import Message
from spade.behaviour import State
from WSN.sensorstrategy import SensorStrategy, ActuatorStrategy, SpreadingStrategy
from base.fsm import BaseFSM
import util.config as cfg
from util.logger import LoggerImpl
from aioxmpp import JID
import json


class NeighboursUpdate(State):
    """
    behavior where the agent updates their contact list dynamically based on the change in the
    network due to both crashes of other nodes that make changes deliberately made by the end user.
    """
    async def run(self):
        # check the neighbours list
        for neighbour in cfg.neighbours["jids"]:
            if JID.fromstr(neighbour) not in self.agent.presence.get_contacts():
                if cfg.logging["enabled"]:
                    self.agent.log.log("Subscription sent to "+neighbour)
                # Send a subscribe request to the agent
                self.presence.subscribe(neighbour)

        # check the contact list
        for neighbour in self.agent.presence.get_contacts():
            if "sensor" in str(neighbour):
                if str(neighbour) not in cfg.neighbours["jids"]:
                    if cfg.logging["enabled"]:
                        self.agent.log.log("Unsubscription sent to "+str(neighbour))
                    # Send a unsubscribe request to the agent
                    self.presence.unsubscribe(str(neighbour))

        self.set_next_state("STATE_ONE")


class SendSensorValues(State):
    """
    Behavior where the agent detects specific data from the environment and sends
    them to the agent prepared for their processing.
    """
    async def run(self):
        msg = Message(to=cfg.jid["dbmanager_agent"])
        msg.set_metadata("performative", "inform")
        msg.set_metadata("service", "detection")
        msg.body = json.dumps(self.agent.sensor_read_strategy.read_sensor_values())
        await self.send(msg)
        self.set_next_state("STATE_TWO")


class MsgReceiver(State):
    """
    Behavior where the agent collects and processes messages from their mailbox,
    communicating with the other agents on the network
    """
    async def run(self):
        msg = await self.receive(timeout=5)
        if msg:
            if self.agent.action.match(msg):
                # Perform Action
                self.agent.set("information", "")
                self.set_next_state("STATE_THREE")
            elif self.agent.spread.match(msg):
                self.agent.set("information", str(msg.body))
                # Spreading
                self.set_next_state("STATE_FOUR")
            else:
                self.set_next_state("STATE_ZERO")
        else:
            self.set_next_state("STATE_ZERO")


class PerformAction(State):
    """
    Behavior where the agent performs a specific action (typically an actuator drive) relating
    to the occurrence of a certain event in the environment or the receipt of a specific
    command from the user the final.
    """
    async def run(self):
        self.agent.actuator_strategy.perform_action(self)
        self.set_next_state("STATE_FOUR")


class SpreadInformation(State):
    """
    Behavior where the agent disseminates specific information to other network nodes
    according to a certain spreading logic.
    """
    async def run(self):
        if await self.agent.spreading_strategy.spreading(self, self.agent.get("information")):
            self.set_next_state("STATE_THREE")
        else:
            self.set_next_state("STATE_ZERO")


class SensorAgentBehav(BaseFSM):
    """
    General agent behavior
    """

    async def on_start(self):
        await super().on_start()
        self.add_state(name="STATE_ZERO", state=NeighboursUpdate(), initial=True)
        self.add_state(name="STATE_ONE", state=SendSensorValues())
        self.add_state(name="STATE_TWO", state=MsgReceiver())
        self.add_state(name="STATE_THREE", state=PerformAction())
        self.add_state(name="STATE_FOUR", state=SpreadInformation())

        self.add_transition(source="STATE_ZERO", dest="STATE_ONE")
        self.add_transition(source="STATE_ONE", dest="STATE_TWO")
        self.add_transition(source="STATE_TWO", dest="STATE_THREE")
        self.add_transition(source="STATE_TWO", dest="STATE_ZERO")
        self.add_transition(source="STATE_TWO", dest="STATE_FOUR")
        self.add_transition(source="STATE_THREE", dest="STATE_FOUR")
        self.add_transition(source="STATE_FOUR", dest="STATE_THREE")
        self.add_transition(source="STATE_FOUR", dest="STATE_ZERO")

        if JID.fromstr(cfg.jid["trigger_agent"]) not in self.agent.presence.get_contacts():
            if cfg.logging["enabled"]:
                self.agent.log.log("Subscription sent to triggeragent")

            # Send a subscribe request to the triggeragent
            self.presence.subscribe(cfg.jid["trigger_agent"])
        else:
            if cfg.logging["enabled"]:
                self.agent.log.log("triggeragent is already in the contact list")

        if JID.fromstr(cfg.jid["dbmanager_agent"]) not in self.agent.presence.get_contacts():
            if cfg.logging["enabled"]:
                self.agent.log.log("Subscription sent to dbmanageragent")
            # Send a subscribe request to the dbmanageragent
            self.presence.subscribe(cfg.jid["dbmanager_agent"])
        else:
            if cfg.logging["enabled"]:
                self.agent.log.log("dbmanageragent is already in the contact list")

        if JID.fromstr(cfg.jid["statistics_agent"]) not in self.agent.presence.get_contacts():
            if cfg.logging["enabled"]:
                self.agent.log.log("Subscription sent to statisticsagent")
            # Send a subscribe request to the statisticsagent
            self.presence.subscribe(cfg.jid["statistics_agent"])
        else:
            if cfg.logging["enabled"]:
                self.agent.log.log("statisticsagent is already in the contact list")

        if JID.fromstr(cfg.jid["nodemanager_agent"]) not in self.agent.presence.get_contacts():
            if cfg.logging["enabled"]:
                self.agent.log.log("Subscription sent to nodemanageragent")
            # Send a subscribe request to the nodemanageragent
            self.presence.subscribe(cfg.jid["nodemanager_agent"])
        else:
            if cfg.logging["enabled"]:
                self.agent.log.log("nodemanageragent is already in the contact list")


class SensorAgent(Agent):
    def __init__(self, agent_jid: str, password: str, spread_param=2):
        """
        :param agent_jid: unique identifier of the agent
        :param password: string used for agent authentication on the xmpp server
        :param spread_param: parameter used by the information spreading logic
        """
        super().__init__(agent_jid, password)
        self.sensor_read_strategy: SensorStrategy
        self.actuator_strategy: ActuatorStrategy
        self.spreading_strategy: SpreadingStrategy
        self.log = LoggerImpl(str(self.jid))
        self.spread_param = spread_param
        self.action = Template()
        self.spread = Template()

    async def setup(self):
        self.action.set_metadata("performative", "request")
        self.action.sender = cfg.jid["trigger_agent"]
        self.spread.set_metadata("performative", "propagate")
        self.add_behaviour(SensorAgentBehav())
