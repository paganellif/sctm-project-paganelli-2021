import datetime
import pymongo
import util.config as cfg
from processing.dbconnectors import *


class DBManagerConnectorImpl(DBManagerConnector):
    def __init__(self, db_url):
        self.__client = pymongo.MongoClient(db_url)
        self.__db_name = self.__client[cfg.database["db_name"]]

    def insert_sensor_value(self, agent_jid: str, data: dict, db_coll: str) -> ObjectId:
        self.check_collection(db_coll)
        document = {"agent_jid": agent_jid}
        if data:
            document.update(data)
        document["timestamp"] = datetime.datetime.now()
        return self.__db_name[db_coll].insert_one(document)

    def get_collection(self, db_coll: str) -> Collection:
        self.check_collection(db_coll)
        return self.__db_name[db_coll]

    def check_collection(self, db_coll: str) -> bool:
        return db_coll in self.__db_name.list_collection_names()

    def insert_node_config(self, agent_jid: str, data: dict) -> ObjectId:
        return self.insert_sensor_value(agent_jid, data, cfg.collections["nodes_configs"])


class DBTriggerConnectorImpl(DBTriggerConnector, DBManagerConnectorImpl):
    def select_last_detections(self, agent_jid: str, limit: int, db_coll: str) -> Cursor:
        self.check_collection(db_coll)
        self.check_limit(limit)
        return self.get_collection(db_coll).find({"agent_jid": agent_jid}).sort("timestamp", -1).limit(int(limit))

    def insert_event_detection(self, agent_jid: str, id_reference: dict) -> ObjectId:
        self.check_collection(cfg.collections["event_detections"])
        return self.insert_sensor_value(agent_jid, id_reference, cfg.collections["event_detections"])

    def insert_error_report(self, agent_jid: str, description: str) -> ObjectId:
        self.check_collection(cfg.collections["failure_reports"])
        document: dict = {"description": description}
        return self.insert_sensor_value(agent_jid, document, cfg.collections["failure_reports"])

    def insert_actuator_triggered(self, agent_jid: str) -> ObjectId:
        self.check_collection(cfg.collections["triggered_actions"])
        return self.insert_sensor_value(agent_jid, {}, cfg.collections["triggered_actions"])

    def check_limit(self, limit: int) -> bool:
        return limit <= 0


class DBStatisticsConnectorImpl(DBStatisticsConnector, DBManagerConnectorImpl):
    def select_distinct_agents_jid(self) -> list:
        self.check_collection(cfg.collections["sensors_detections"])
        return self.get_collection(cfg.collections["sensors_detections"]).distinct("agent_jid")

    def insert_aggregation(self, agent_jid: str, keys: list) -> ObjectId:
        stats_coll = cfg.collections["detection_statistics"]
        sensor_values_coll = cfg.collections["sensors_detections"]
        self.check_collection(stats_coll)
        self.check_collection(sensor_values_coll)

        """
        if keys:
            if not isinstance(keys, list):
                # TODO cannot stop execution -> handle this case in another way
                raise ValueError("keys must be a list of string")
            if len(keys) == 0:
                # TODO cannot stop execution -> handle this case in another way
                raise ValueError("keys must contain at least an item")
        else:
            # TODO cannot stop execution -> handle this case in another way
            raise ValueError("keys must be a list of string")
        """

        group: dict = dict()
        group["_id"] = "$agent_jid"

        for key in keys:
            # Average aggregation
            group[key + "_avg"] = {"$avg": "$" + key}
            # Max aggregation
            group[key + "_max"] = {"$max": "$" + key}
            # Min aggregation
            group[key + "_min"] = {"$min": "$" + key}

        pipeline: list = list()
        pipeline.append({"$group": group})
        pipeline.append({"$match": {"_id": agent_jid}})
        res = self.get_collection(sensor_values_coll).aggregate(pipeline=pipeline)
        aggregation_res: dict = res.next()
        aggregation_res.pop("_id")

        return self.insert_sensor_value(agent_jid, aggregation_res, stats_coll)


class DBFrontEndConnectorImpl(DBFrontEndConnector, DBTriggerConnectorImpl, DBStatisticsConnectorImpl):
    def select_last_statistics(self, agent_jid: str, limit: int) -> Cursor:
        return self.select_last_detections(agent_jid, limit, cfg.collections["detection_statistics"])

    def select_node_config(self, agent_jid: str) -> Cursor:
        return self.select_last_detections(agent_jid, 1, cfg.collections["nodes_configs"])
