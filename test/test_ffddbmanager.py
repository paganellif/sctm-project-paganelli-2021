import asyncio
import json
import unittest

from aioxmpp import JID
from spade.behaviour import OneShotBehaviour
from spade.message import Message
import util.config as cfg
from processing.ffddbmanageragent import FFDDBManagerAgent
from utilities import MockedAgentFactory, BaseAgentTestCase


class FFDDBManagerTestCase(BaseAgentTestCase):
    def setUp(self) -> None:
        self.db_manager = FFDDBManagerAgent("dbmanager@"+cfg.xmpp["hostname"], "qwertyqwerty")

    def test_init_db_manager(self):
        self.assertIsNotNone(self.db_manager)
        self.assertEqual(self.db_manager.jid, JID.fromstr("dbmanager@"+cfg.xmpp["hostname"]))

    def test_initial_contacts_no_sensors(self):
        self.db_manager.start().result()
        contacts = self.db_manager.presence.get_contacts()
        self.assertEqual(0, len(contacts))
        self.db_manager.stop().result()

    def test_receive_insert_detection(self):
        self.db_manager.start().result()
        fake_sensor = MockedAgentFactory(jid=cfg.jid["test_sensor_agent"])

        class SendBehaviour(OneShotBehaviour):
            async def run(self):
                msg = Message(to="dbmanager@"+cfg.xmpp["hostname"])
                msg.set_metadata("performative", "inform")
                msg.body = json.dumps({})
                await self.send(msg)
                await asyncio.sleep(3)
                self.kill()

        behaviour = SendBehaviour()
        fake_sensor.add_behaviour(behaviour)
        fake_sensor.start().result()
        behaviour.join()

        query = {"agent_jid": cfg.jid["test_sensor_agent"]}
        result = self.db_manager.db_conn.get_collection(cfg.collections["sensors_detections"]).find(query)
        self.assertEqual(result.count(), 1)

        self.db_manager.db_conn.get_collection(cfg.collections["sensors_detections"]).delete_many(query)
        self.db_manager.stop().result()

    def test_check_strategy_bad_detection(self):
        bad_detection = {"temp": float('nan')}
        check = self.db_manager.check_strategy.check_values(bad_detection)
        self.assertFalse(check)

    def test_check_strategy_bad_detections(self):
        bad_detection = {"temp": float('nan'), "hum": float('nan')}
        check = self.db_manager.check_strategy.check_values(bad_detection)
        self.assertFalse(check)

    def test_check_strategy_good_detection(self):
        good_detection = {"temp": 30}
        check = self.db_manager.check_strategy.check_values(good_detection)
        self.assertTrue(check)

    def test_inform_trigger(self):
        self.db_manager.start().result()
        fake_sensor = MockedAgentFactory(jid=cfg.jid["test_sensor_agent"])
        fake_trigger = MockedAgentFactory(jid="trigger@"+cfg.xmpp["hostname"])

        class SendBehaviour(OneShotBehaviour):
            async def run(self):
                msg = Message(to="dbmanager@"+cfg.xmpp["hostname"])
                msg.set_metadata("performative", "inform")
                msg.body = json.dumps({})
                await self.send(msg)
                await asyncio.sleep(3)
                self.kill()

        class RecvBehaviour(OneShotBehaviour, unittest.TestCase):
            async def run(self):
                msg = await self.receive(timeout=10)
                self.assertIsNotNone(msg)
                self.assertEqual(msg.to, JID.fromstr("trigger@"+cfg.xmpp["hostname"]))
                self.assertEqual(msg.sender, "dbmanager@"+cfg.xmpp["hostname"])
                self.assertIsNotNone(msg.body)
                self.assertEqual(msg.get_metadata("performative"), "inform")
                self.kill()

        send_behav = SendBehaviour()
        rcv_behav = RecvBehaviour()
        fake_sensor.add_behaviour(send_behav)
        fake_trigger.add_behaviour(rcv_behav)
        fake_sensor.start().result()
        fake_trigger.start().result()
        send_behav.join()
        rcv_behav.join()

        query = {"agent_jid": cfg.jid["test_sensor_agent"]}
        self.db_manager.db_conn.get_collection(cfg.collections["sensors_detections"]).delete_many(query)

        self.db_manager.stop().result()
