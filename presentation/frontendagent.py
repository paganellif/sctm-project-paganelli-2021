import json
import os
from spade.agent import Agent
from spade.behaviour import State
from spade.template import Template
from util.logger import LoggerImpl
from base.fsm import BaseFSM
from processing.dbconnfactory import DBConnFactory
from presentation.routehandler import RouteHandler
import util.config as cfg


class StartServer(State):
    """
    Initial behaviour that starts asynchronously the web server by
    using the configurations specified in the config file
    """
    async def run(self):
        self.agent.web.start(hostname=cfg.web["hostname"], port=cfg.web["port"], templates_path="presentation/templates")
        if self.agent.web.is_started() and cfg.logging["enabled"]:
            self.agent.log.log("Web server listening on http://"+cfg.web["hostname"]+":"+str(cfg.web["port"]))

        self.set_next_state("STATE_TWO")


class StationsStateUpdate(State):
    """
    Behavior where communications with network agents take place and the status of the nodes is updated.
    """

    async def run(self):
        msg = await self.receive(timeout=3)
        if msg:
            if self.agent.states_update.match(msg):
                if cfg.logging["enabled"] is True:
                    self.agent.log.log("Received the update of the sensoragent states from the triggeragent")
                
                body: dict = json.loads(str(msg.body))
                self.agent.stations_status.update(body)
        else:
            if cfg.logging["enabled"] is True:
                self.agent.log.log("No msg received :(")

        self.set_next_state("STATE_TWO")


class FrontEndAgentBehav(BaseFSM):
    """
    General agent behavior
    """
    async def on_start(self):
        await super().on_start()
        self.add_state(name="STATE_ONE", state=StartServer(), initial=True)
        self.add_state(name="STATE_TWO", state=StationsStateUpdate())

        self.add_transition(source="STATE_ONE", dest="STATE_TWO")
        self.add_transition(source="STATE_TWO", dest="STATE_TWO")


class FrontEndAgent(Agent):
    def __init__(self, agent_jid: str, password: str):
        """
        :param agent_jid: unique identifier of the agent
        :param password: string used for agent authentication on the xmpp server
        """
        super().__init__(agent_jid, password)
        self.route_handler = RouteHandler(self)
        self.db_conn = DBConnFactory().create_front_end_db_connector()
        self.log = LoggerImpl(str(self.jid))
        self.stations_status: dict = dict()
        self.states_update = Template()

    async def setup(self):
        for jid in list(self.db_conn.select_distinct_agents_jid()):
            self.stations_status[jid] = "Working"
        self.web.app['static_root_url'] = "/static/"
        root_dir = os.path.dirname(os.path.abspath(__file__))
        self.web.app.router.add_static('/static/', path=str(root_dir+"/static"), name='static')
        self.web.add_get("/", self.route_handler.home, "index.html")
        self.web.add_get("/value/{jid}", self.route_handler.value, None)
        self.web.add_get("/wsn", self.route_handler.wsn, None)
        self.web.add_get("/statistics/{jid}", self.route_handler.statistics, None)
        self.web.add_get("/node_info/{jid}", self.route_handler.node_info, None)
        self.web.add_post("/node/update/{jid}", self.route_handler.node_update, None)

        self.states_update.set_metadata("performative", "inform")
        self.states_update.sender = cfg.jid["trigger_agent"]

        self.add_behaviour(FrontEndAgentBehav())
