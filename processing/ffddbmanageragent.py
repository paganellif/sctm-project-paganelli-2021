import math

from processing.dbmanageragent import DBManagerAgent
from processing.dbmanagerstrategy import DBManagerStrategy


class DBManagerStrategyImpl(DBManagerStrategy):
    def check_values(self, values: dict) -> bool:
        for value in values.values():
            if math.isnan(value):
                return False
        return True


class FFDDBManagerAgent(DBManagerAgent):
    def __init__(self, agent_jid: str, password: str):
        super().__init__(agent_jid, password)
        self.check_strategy = DBManagerStrategyImpl()
