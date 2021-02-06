import asyncio
from spade.agent import Agent
from spade.behaviour import State
from base.fsm import BaseFSM
from processing.dbconnfactory import DBConnFactory
import util.config as cfg
from util.logger import LoggerImpl


class InsertStatistics(State):
    """
    Behavior where the agent calculates the aggregations on the detections made of SensorAgents
    """
    async def run(self):
        for agent in self.agent.db_conn.select_distinct_agents_jid():
            if cfg.logging["enabled"] is True:
                self.agent.log.log("Inserting statistics for agent: "+str(agent))
            self.agent.db_conn.insert_aggregation(str(agent), self.agent.keys)
        await asyncio.sleep(self.agent.period)
        self.set_next_state("STATE_ONE")


class StatisticsAgentBehav(BaseFSM):
    """
    General agent behavior
    """
    async def on_start(self):
        await super().on_start()
        self.add_state(name="STATE_ONE", state=InsertStatistics(), initial=True)

        self.add_transition(source="STATE_ONE", dest="STATE_ONE")


class StatisticsAgent(Agent):
    def __init__(self, agent_jid, password, period=60):
        """
        :param agent_jid: unique identifier of the agent
        :param password: string used for agent authentication on the xmpp server
        :param period: period of execution of the agent's behavior
        """
        super().__init__(agent_jid, password)
        self.log = LoggerImpl(str(self.jid))
        self.db_conn = DBConnFactory().create_statistics_db_connector()
        self.period = period
        self.keys: list = list()

        for name in cfg.parameters.values():
            self.keys.append(name)

    async def setup(self):
        self.add_behaviour(StatisticsAgentBehav())
