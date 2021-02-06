import asyncio

import pytest
from aioxmpp import JID
import util.config as cfg
from WSN.ffdsensoragent import FFDSensorAgent
from processing.statisticsagent import StatisticsAgent
from utilities import BaseAgentTestCase


class StatisticsTestCase(BaseAgentTestCase):
    def setUp(self) -> None:
        self.statistics = StatisticsAgent(cfg.jid["statistics_agent"], "qwertyqwerty")

    def test_init_statistics(self):
        self.assertIsNotNone(self.statistics)
        self.assertEqual(self.statistics.jid, JID.fromstr(cfg.jid["statistics_agent"]))

    @pytest.mark.asyncio
    async def test_add_sensor_contact_list(self):
        fake_sensor = FFDSensorAgent(agent_jid=cfg.jid["test_sensor_agent"], password="qwertyqwerty")
        fake_sensor.start().result()

        self.statistics.start(auto_register=True).result()
        fake_sensor.presence.subscribe(cfg.jid["statistics_agent"])
        await asyncio.sleep(2)
        self.assertEqual(len(self.statistics.presence.get_contacts()), 1)
        self.assertIn(JID.fromstr(cfg.jid["test_sensor_agent"]), self.statistics.presence.get_contacts())

        fake_sensor.stop().result()
        self.statistics.start(auto_register=True).result()

    @pytest.mark.asyncio
    async def test_insert_statistic(self):
        fake_agent = cfg.jid["test_sensor_agent"]
        self.statistics.db_conn.insert_sensor_value(fake_agent, {}, cfg.collections["sensors_detections"])

        self.statistics.start(auto_register=True).result()
        await asyncio.sleep(5)

        query = {"agent_jid": fake_agent}
        result = self.statistics.db_conn.get_collection(cfg.collections["detection_statistics"]).find(query)
        self.assertGreaterEqual(result.count(), 1)

        self.statistics.db_conn.get_collection(cfg.collections["sensors_detections"]).delete_many(query)
        self.statistics.db_conn.get_collection(cfg.collections["detection_statistics"]).delete_many(query)
        self.statistics.stop().result()
