from abc import ABC, abstractmethod


class DBManagerStrategy(ABC):
    @abstractmethod
    def check_values(self, values: dict) -> bool:
        """
        Validates passed values according to a certain logic
        :param values: values that need to be checked
        :return: true if the passed values respect the verification logic, otherwise false
        """
        pass
