from processing.dbconnectorimpl import *


class DBConnAbstractFactory(ABC):
    @abstractmethod
    def create_manager_db_connector(self) -> DBManagerConnector:
        """

        :return:
        """
        pass

    @abstractmethod
    def create_trigger_db_connector(self) -> DBTriggerConnector:
        """

        :return:
        """
        pass

    @abstractmethod
    def create_statistics_db_connector(self) -> DBStatisticsConnector:
        """

        :return:
        """
        pass

    @abstractmethod
    def create_front_end_db_connector(self) -> DBFrontEndConnector:
        """

        :return:
        """
        pass


class DBConnFactory(DBConnAbstractFactory):

    def create_manager_db_connector(self) -> DBManagerConnector:
        return DBManagerConnectorImpl(cfg.database["dbmanager_url"])

    def create_trigger_db_connector(self) -> DBTriggerConnector:
        return DBTriggerConnectorImpl(cfg.database["trigger_url"])

    def create_statistics_db_connector(self) -> DBStatisticsConnector:
        return DBStatisticsConnectorImpl(cfg.database["statistics_url"])

    def create_front_end_db_connector(self) -> DBFrontEndConnector:
        return DBFrontEndConnectorImpl(cfg.database["frontend_url"])
