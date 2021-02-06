import json

from aiohttp.web_request import Request
from pymongo.collection import Collection
from spade.message import Message
import util.config as cfg
from aiohttp import web


class RouteHandler:
    def __init__(self, agent):
        self.__agent = agent

    async def home(self, request: Request):
        """
        Web application entry point: it render the initial template
        """
        return None

    async def wsn(self, request: Request):
        """
        Route GET /wsn
        :return: an object containing the jids of the SensorAgents.
        """
        jids: list = list(self.__agent.db_conn.select_distinct_agents_jid())
        response = json.dumps({"agents_jid": jids})
        return response

    async def value(self, request: Request):
        """
        Route GET /value/{jid}
        :return: the detections made by the SensorAgent identified by the specified jid.
        """
        agent_jid = request.match_info["jid"]
        response: list = list()
        if agent_jid:
            if agent_jid not in self.__agent.stations_status.keys():
                raise web.HTTPBadRequest()
            if "limit" in request.rel_url.query.keys():
                limit = int(request.rel_url.query["limit"])
                if limit < 1:
                    raise web.HTTPBadRequest()
            else:
                limit = 1
            res = self.__agent.db_conn.select_last_detections(agent_jid, limit, cfg.collections["sensors_detections"])
            for doc in res:
                doc.pop("_id")
                doc["timestamp"] = doc.pop("timestamp").__str__()
                response.append(doc)
            return response
        else:
            raise web.HTTPBadRequest()

    async def state(self, request: Request):
        """
        Route GET /state/{jid}
        :return: the state of the SensorAgent identified by the specified jid.
        """
        agent_jid = request.match_info["jid"]
        if agent_jid:
            if agent_jid not in self.__agent.stations_status.keys():
                raise web.HTTPBadRequest()
            status = self.__agent.stations_status[agent_jid]
            response = {"state": status}
            return response
        else:
            raise web.HTTPBadRequest()

    async def statistics(self, request: Request):
        """
        Route GET /statistics/{jid}
        :return: the statistics made for the SensorAgent identified by the specified jid.
        """
        agent_jid = request.match_info["jid"]
        response: list = list()
        if agent_jid:
            if agent_jid not in self.__agent.stations_status.keys():
                raise web.HTTPBadRequest()
            if "limit" in request.rel_url.query.keys():
                limit = int(request.rel_url.query["limit"])
                if limit < 1:
                    raise web.HTTPBadRequest()
            else:
                limit = 1
            res = self.__agent.db_conn.select_last_statistics(agent_jid, limit)

            if res:
                for doc in res:
                    doc.pop("_id")
                    doc["timestamp"] = doc.pop("timestamp").__str__()
                    response.append(doc)
                return response
            else:
                raise web.HTTPBadRequest()
        else:
            raise web.HTTPBadRequest()

    async def node_info(self, request: Request):
        """
        Route GET /node_info/{jid}
        :return: an object containing a configuration subset of the node where is located the
        agent identified by the specified jid.
        """
        agent_jid = request.match_info["jid"]
        if agent_jid:
            tokens = agent_jid.split("@")
            tmp = tokens[0].split(".")
            target = "nodemanager." + tmp[1] + "." + tmp[2] + "@" + cfg.xmpp["hostname"]
            print(target)
            res = self.__agent.db_conn.select_node_config(target)
            if res:
                doc = res[0]
                doc.pop("_id")
                doc["timestamp"] = doc.pop("timestamp").__str__()
                return doc
            else:
                raise web.HTTPBadRequest()
        else:
            raise web.HTTPBadRequest()

    async def node_update(self, request: Request):
        """
        Route POST /node/update/{jid}
        Update a configuration subset of the node that has the name passed
        :return: request result [200,400]
        """
        agent_jid = request.match_info["jid"]
        if agent_jid and request.can_read_body:
            tokens = agent_jid.split(".")
            msg = Message(to="nodemanager." + tokens[1] + "@" + cfg.xmpp["hostname"])
            msg.set_metadata("performative", "request")
            msg.body = str(await request.text())  # json.dumps(request.json())
            print(msg.body)
            await self.__agent.behaviours[0].send(msg)
            raise web.HTTPOk()
        else:
            raise web.HTTPBadRequest()

