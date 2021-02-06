import asyncio

import aiohttp
import pytest
from aioxmpp import JID
import util.config as cfg
from presentation.frontendagent import FrontEndAgent
from utilities import BaseAgentTestCase


class FrontEndTestCase(BaseAgentTestCase):
    def setUp(self) -> None:
        self.front_end = FrontEndAgent(cfg.jid["frontend_agent"], "qwertyqwerty")

    @pytest.mark.serial
    def test_init_front_end(self):
        self.assertIsNotNone(self.front_end)
        self.assertEqual(self.front_end.jid, JID.fromstr(cfg.jid["frontend_agent"]))

    @pytest.mark.serial
    def test_initial_contacts_no_sensors(self):
        self.front_end.start(auto_register=True).result()
        contacts = self.front_end.presence.get_contacts()
        self.assertEqual(0, len(contacts))
        self.front_end.stop().result()

    @pytest.mark.asyncio
    @pytest.mark.serial
    async def test_web_server_is_started(self):
        self.front_end.start(auto_register=True).result()
        await asyncio.sleep(3)
        self.assertTrue(self.front_end.web.is_started())
        self.front_end.stop().result()

    @pytest.mark.asyncio
    @pytest.mark.serial
    async def test_web_server_port_hostname(self):
        self.front_end.start(auto_register=True).result()
        await asyncio.sleep(3)
        self.assertEqual(self.front_end.web.hostname, "localhost")
        self.assertEqual(self.front_end.web.port, 8080)
        self.front_end.stop().result()

    @pytest.mark.serial
    def test_init_station_status(self):
        self.assertEqual(len(self.front_end.stations_status.values()), 0)

    @pytest.mark.asyncio
    @pytest.mark.serial
    async def test_station_status_sensors(self):
        self.front_end.db_conn.insert_sensor_value("fake_sensor", {}, cfg.collections["sensors_detections"])

        self.front_end.start(auto_register=True).result()
        await asyncio.sleep(3)
        self.assertIn("fake_sensor", self.front_end.stations_status.keys())
        self.assertEqual("Working", self.front_end.stations_status.get("fake_sensor"))

        query = {"agent_jid": "fake_sensor"}
        self.front_end.db_conn.get_collection(cfg.collections["sensors_detections"]).delete_one(query)
        self.front_end.stop().result()

    @pytest.mark.asyncio
    @pytest.mark.serial
    async def test_home_route(self):
        self.front_end.start(auto_register=True).result()
        await asyncio.sleep(3)

        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8080/') as resp:
                self.assertEqual(200, resp.status)
                self.assertEqual("text/html", resp.content_type)

        self.front_end.stop().result()

    @pytest.mark.asyncio
    @pytest.mark.serial
    async def test_wsn_route(self):
        self.front_end.start(auto_register=True).result()
        await asyncio.sleep(3)

        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8080/wsn') as resp:
                self.assertEqual(200, resp.status)
                self.assertEqual("application/json", resp.content_type)

        self.front_end.stop().result()

    @pytest.mark.asyncio
    @pytest.mark.serial
    async def test_value_route(self):
        self.front_end.start(auto_register=True).result()
        await asyncio.sleep(3)

        self.front_end.db_conn.insert_sensor_value("fake_sensor", {}, cfg.collections["sensors_detections"])
        self.front_end.stations_status.update({"fake_sensor": "Working"})

        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8080/value/fake_sensor') as resp:
                self.assertEqual(200, resp.status)
                self.assertEqual("application/json", resp.content_type)
            async with session.get('http://localhost:8080/value/fake_sensor?limit=10') as resp:
                self.assertEqual(200, resp.status)
                self.assertEqual("application/json", resp.content_type)
            async with session.get('http://localhost:8080/value/fake_sensor?limit=-1') as resp:
                self.assertEqual(400, resp.status)

        query = {"agent_jid": "fake_sensor"}
        self.front_end.db_conn.get_collection(cfg.collections["sensors_detections"]).delete_one(query)

        self.front_end.stop().result()

    @pytest.mark.asyncio
    @pytest.mark.serial
    async def test_state_route(self):
        self.front_end.start(auto_register=True).result()
        await asyncio.sleep(3)

        self.front_end.stations_status.update({"fake_sensor": "Working"})

        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8080/state') as resp:
                self.assertEqual(404, resp.status)

            async with session.get('http://localhost:8080/state/fake_sensor') as resp:
                self.assertEqual(200, resp.status)
                self.assertEqual("application/json", resp.content_type)

        self.front_end.stop().result()

    @pytest.mark.asyncio
    @pytest.mark.serial
    async def test_statistics_route(self):
        self.front_end.start(auto_register=True).result()
        await asyncio.sleep(3)
        self.front_end.stations_status.update({"fake_sensor": "Working"})
        self.front_end.db_conn.insert_sensor_value("fake_sensor", {}, cfg.collections["detection_statistics"])

        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8080/statistics') as resp:
                self.assertEqual(404, resp.status)
            async with session.get('http://localhost:8080/statistics/fake_sensor') as resp:
                self.assertEqual(200, resp.status)
                self.assertEqual("application/json", resp.content_type)
            async with session.get('http://localhost:8080/statistics/fake_sensor?limit=10') as resp:
                self.assertEqual(200, resp.status)
                self.assertEqual("application/json", resp.content_type)
            async with session.get('http://localhost:8080/statistics/fake_sensor?limit=-1') as resp:
                self.assertEqual(400, resp.status)

        query = {"agent_jid": "fake_sensor"}
        self.front_end.db_conn.get_collection(cfg.collections["detection_statistics"]).delete_one(query)

        self.front_end.stop().result()
