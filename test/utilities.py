import unittest

import factory
from asynctest import CoroutineMock, Mock

from spade.agent import Agent
from spade.container import Container
from spade import quit_spade


class BaseAgentTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        container = Container()
        if not container.is_running:
            container.__init__()

    @classmethod
    def tearDownClass(cls) -> None:
        quit_spade()


class MockedConnectedAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._async_connect = CoroutineMock()
        self._async_register = CoroutineMock()
        self.conn_coro = Mock()
        self.conn_coro.__aexit__ = CoroutineMock()
        self.stream = Mock()


class MockedAgentFactory(factory.Factory):
    class Meta:
        model = MockedConnectedAgent

    jid = "fake@jid"
    password = "fake_password"
