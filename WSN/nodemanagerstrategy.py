from abc import ABC, abstractmethod


class CheckConfigStrategy(ABC):
    @abstractmethod
    def check_config(self, values: dict) -> bool:
        """
        Strategy that defines the logic used to validate the values to be set in the node configuration
        :return: true if the passed values satisfy the defined conditions, otherwise false
        """
        pass


class GetConfigStrategy(ABC):
    @abstractmethod
    def get_config(self) -> dict:
        """
        :return: an object containing the node configuration
        """
        pass
