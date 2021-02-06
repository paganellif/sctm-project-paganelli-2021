import unittest
from processing.dbconnfactory import DBConnFactory
from processing.dbconnectors import DBManagerConnector, DBTriggerConnector, DBStatisticsConnector, DBFrontEndConnector


class DBConnectorFactoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = DBConnFactory()

    def test_create_manager_db_connector(self):
        db_manager_conn = self.factory.create_manager_db_connector()
        self.assertIsNotNone(db_manager_conn)
        self.assertIsInstance(db_manager_conn, DBManagerConnector)

    def test_create_trigger_db_connector(self):
        trigger_conn = self.factory.create_trigger_db_connector()
        self.assertIsNotNone(trigger_conn)
        self.assertIsInstance(trigger_conn, DBTriggerConnector)

    def test_create_statistics_db_connector(self):
        stats_conn = self.factory.create_statistics_db_connector()
        self.assertIsNotNone(stats_conn)
        self.assertIsInstance(stats_conn, DBStatisticsConnector)

    def test_create_front_end_db_connector(self):
        frontend_conn = self.factory.create_front_end_db_connector()
        self.assertIsNotNone(frontend_conn)
        self.assertIsInstance(frontend_conn, DBFrontEndConnector)
