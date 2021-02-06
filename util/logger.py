from abc import ABC, abstractmethod
import logging
import util.config as cfg


class Logger(ABC):
    @abstractmethod
    def log(self, msg: str) -> None:
        pass


class LoggerImpl(Logger):
    def __init__(self, agent_jid: str):
        # logging.basicConfig(level=cfg.logging["level"])
        self.__logger = logging.getLogger(agent_jid)
        self.__agent_jid = agent_jid

    def log(self, msg: str) -> None:
        print('\n[' + self.__agent_jid + '] ' + msg)
        self.__logger.debug(msg)
