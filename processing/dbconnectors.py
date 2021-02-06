from abc import ABC, abstractmethod
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.cursor import Cursor


class DBManagerConnector(ABC):
    @abstractmethod
    def insert_sensor_value(self, agent_jid: str, data: dict, db_coll: str) -> ObjectId:
        """

        :param agent_jid: the identifier of the agent who performed the read
        :param data: the reading data
        :param db_coll: the name of the collection in which the document is to be inserted
        :return: ObjectId: the ObjectId of the inserted document otherwise None
        """
        pass

    @abstractmethod
    def get_collection(self, db_coll: str) -> Collection:
        """

        :param db_coll: the name of the collection
        :return: Collection: the collection with the name db_coll otherwise None
        """
        pass

    @abstractmethod
    def check_collection(self, db_coll: str) -> bool:
        """

        :param db_coll: the name of the collection
        :return: boolean: True if there is a collection with the name db_coll otherwise False
        """
        pass

    @abstractmethod
    def insert_node_config(self, agent_jid: str, data: dict) -> ObjectId:
        """

        :param agent_jid: jid of the agent for which the node configuration is to be entered
        :param data: node configuration values to insert
        :return: ObjectId: the ObjectId of the inserted document otherwise None
        """
        pass


class DBTriggerConnector(ABC):
    @abstractmethod
    def select_last_detections(self, agent_jid: str, limit: int, db_coll: str) -> Cursor:
        """

        :param agent_jid: the identifier of the agent who performed the request
        :param limit: number of detections to be retrieved
        :param db_coll: the name of the collection
        :return: Cursor: a cursor containing the the latest limit detections
        """
        pass

    @abstractmethod
    def insert_event_detection(self, agent_jid: str, id_reference: dict) -> ObjectId:
        """

        :param agent_jid: the identifier of the agent who performed the request
        :param id_reference: data containing the reference of the readings that caused the event detection
        :return: ObjectId: the ObjectId of the inserted document otherwise None
        """
        pass

    @abstractmethod
    def insert_error_report(self, agent_jid: str, description: str) -> ObjectId:
        """

        :param agent_jid: the identifier of the agent who performed the request
        :param description: textual description of the error occurred
        :return: ObjectId: the ObjectId of the inserted document otherwise None
        """
        pass

    @abstractmethod
    def insert_actuator_triggered(self, agent_jid: str) -> ObjectId:
        """

        :param agent_jid: the identifier of the agent who triggered its actuator
        :return: ObjectId: the ObjectId of the inserted document otherwise None
        """
        pass

    @abstractmethod
    def check_limit(self, limit: int) -> bool:
        """

        :param limit: value indicating the maximum number of documents that must be returned
        :return: true if the limit parameter matches the condition, false otherwise
        """
        pass


class DBStatisticsConnector(ABC):
    @abstractmethod
    def select_distinct_agents_jid(self) -> list:
        """
        :return: an object containing the list of SensorAgent jids
        """
        pass

    @abstractmethod
    def insert_aggregation(self, agent_jid: str, keys: list) -> ObjectId:
        """

        :param agent_jid: jid of the agent for which the aggregation is to be performed
        :param keys: list of parameters on which to aggregate
        :return: ObjectId: the ObjectId of the inserted document otherwise None
        """
        pass


class DBFrontEndConnector(ABC):
    @abstractmethod
    def select_last_statistics(self, agent_jid: str, limit: int) -> Cursor:
        """

        :param agent_jid: agent for which the aggregations made are to be returned
        :param limit: number of aggregations to be returned
        :return: Cursor: a Cursor containing the inserted aggregations otherwise None
        """
        pass

    @abstractmethod
    def select_node_config(self, agent_jid: str) -> Cursor:
        """

        :param agent_jid: jid of the agent for which the node configuration is to be returned
        :return: Cursor: a Cursor containing the node config otherwise None
        """
        pass
