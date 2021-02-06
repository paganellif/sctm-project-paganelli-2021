import asyncio
import json

from aioxmpp import JID
from spade.behaviour import OneShotBehaviour
from spade.message import Message
import util.config as cfg
from processing.ffdtriggeragent import FFDTriggerAgent
from utilities import BaseAgentTestCase, MockedAgentFactory


class FFDTriggerTestCase(BaseAgentTestCase):
    def setUp(self) -> None:
        self.trigger = FFDTriggerAgent("trigger@"+cfg.xmpp["hostname"], "qwertyqwerty")

    def test_init_trigger(self):
        self.assertIsNotNone(self.trigger)
        self.assertEqual(self.trigger.jid, JID.fromstr("trigger@"+cfg.xmpp["hostname"]))

    def test_initial_contacts_no_sensors(self):
        self.trigger.start(auto_register=True).result()
        contacts = self.trigger.presence.get_contacts()
        self.assertEqual(0, len(contacts))
        self.trigger.stop().result()

    def test_insert_event_detection(self):
        self.trigger.start(auto_register=True).result()
        query = {"agent_jid": "fake_sensor"}
        self.trigger.db_conn.get_collection(cfg.collections["event_detections"]).delete_many(query)
        fake_db_manager = MockedAgentFactory(jid="dbmanager@"+cfg.xmpp["hostname"])

        class SendBehaviour(OneShotBehaviour):
            async def run(self):
                msg = Message(to="trigger@"+cfg.xmpp["hostname"])
                msg.set_metadata("performative", "inform")
                msg.body = json.dumps({"agent_jid": "fake_sensor"})
                await self.send(msg)
                await asyncio.sleep(3)
                self.kill()

        behaviour = SendBehaviour()
        fake_db_manager.add_behaviour(behaviour)
        fake_db_manager.start().result()
        behaviour.join()

        result = self.trigger.db_conn.get_collection(cfg.collections["event_detections"]).find(query)
        self.assertEqual(result.count(), 1)

        self.trigger.db_conn.get_collection(cfg.collections["event_detections"]).delete_many(query)
        self.trigger.stop().result()

    def test_event_detection_check_strategy(self):
        self.trigger.start(auto_register=True).result()

        attempts = 10
        for i in range(0, attempts):
            self.trigger.db_conn.insert_event_detection("fake_sensor", {}, cfg.collections["event_detections"])

        fake_db_manager = MockedAgentFactory(jid="dbmanager@"+cfg.xmpp["hostname"])

        class SendBehaviour(OneShotBehaviour):
            async def run(self):
                msg = Message(to="trigger@"+cfg.xmpp["hostname"])
                msg.set_metadata("performative", "inform")
                msg.body = json.dumps({"agent_jid": "fake_sensor"})
                await self.send(msg)
                await asyncio.sleep(3)
                self.kill()

        behaviour = SendBehaviour()
        fake_db_manager.add_behaviour(behaviour)
        fake_db_manager.start().result()
        behaviour.join()

        query = {"agent_jid": "fake_sensor"}
        result = self.trigger.db_conn.get_collection(cfg.collections["triggered_actions"]).find(query)
        self.assertGreaterEqual(result.count(), 1)

        self.trigger.db_conn.get_collection(cfg.collections["triggered_actions"]).delete_many(query)
        self.trigger.stop().result()


