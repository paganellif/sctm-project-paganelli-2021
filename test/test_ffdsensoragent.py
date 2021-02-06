import asyncio
import unittest

from spade.behaviour import OneShotBehaviour
from spade.message import Message
import util.config as cfg
from WSN.ffdsensoragent import FFDSensorAgent, SensorStrategyImpl, ActuatorStrategyImpl, SpreadingStrategyImpl
from aioxmpp import JID
from utilities import MockedAgentFactory, BaseAgentTestCase


class FFDSensorAgentTestCase(BaseAgentTestCase):
    def setUp(self) -> None:
        self.sensor_agent = FFDSensorAgent(agent_jid=cfg.jid["test_sensor_agent"], password="qwertyqwerty")

    def test_create_sensor_agent(self):
        self.assertEqual(self.sensor_agent.jid, JID.fromstr(cfg.jid["test_sensor_agent"]))

    def test_start_sensor_agent(self):
        self.sensor_agent.start(auto_register=True).result()
        self.assertTrue(self.sensor_agent.is_alive())
        self.sensor_agent.stop().result()

    def test_initial_strategies(self):
        self.assertIsInstance(self.sensor_agent.sensor_read_strategy, SensorStrategyImpl)
        self.assertIsInstance(self.sensor_agent.actuator_strategy, ActuatorStrategyImpl)
        self.assertIsInstance(self.sensor_agent.spreading_strategy, SpreadingStrategyImpl)

    def test_sensor_values_strategy(self):
        values = self.sensor_agent.sensor_read_strategy.read_sensor_values()
        self.assertIsNotNone(values)
        self.assertIsInstance(values, dict)

    def test_initial_contacts_sensor_agents(self):
        self.sensor_agent.start(auto_register=True).result()
        contacts = self.sensor_agent.presence.get_contacts()
        self.assertIn(JID.fromstr("trigger@"+cfg.xmpp["hostname"]), contacts)
        self.assertIn(JID.fromstr("dbmanager@"+cfg.xmpp["hostname"]), contacts)
        self.assertIn(JID.fromstr("statistics@"+cfg.xmpp["hostname"]), contacts)
        self.sensor_agent.stop().result()

    def test_send_sensor_values(self):
        fake_db_manager = MockedAgentFactory(jid="dbmanager@"+cfg.xmpp["hostname"])

        class RecvBehaviour(OneShotBehaviour, unittest.TestCase):
            async def run(self):
                msg = await self.receive(timeout=10)
                self.assertIsNotNone(msg)
                self.assertEqual(msg.to, JID.fromstr("dbmanager@"+cfg.xmpp["hostname"]))
                self.assertEqual(msg.sender, cfg.jid["test_sensor_agent"])
                self.assertIsNotNone(msg.body)
                self.assertEqual(msg.get_metadata("performative"), "inform")

                self.kill()

        behaviour = RecvBehaviour()

        fake_db_manager.add_behaviour(behaviour)
        fake_db_manager.start().result()
        self.sensor_agent.start(auto_register=True).result()
        behaviour.join()
        self.sensor_agent.stop().result()

    def test_perform_actuator_action(self):
        fake_trigger = MockedAgentFactory(jid="trigger@"+cfg.xmpp["hostname"])

        class SendBehaviour(OneShotBehaviour):
            async def run(self):
                msg = Message(to=cfg.jid["test_sensor_agent"])
                msg.set_metadata("performative", "request")
                await self.send(msg)
                await asyncio.sleep(2)
                self.kill()

        behaviour = SendBehaviour()

        fake_trigger.add_behaviour(behaviour)
        self.sensor_agent.start(auto_register=True).result()
        fake_trigger.start().result()
        behaviour.join()
        self.assertEqual(2, len(self.sensor_agent.behaviours))

        self.sensor_agent.stop().result()
