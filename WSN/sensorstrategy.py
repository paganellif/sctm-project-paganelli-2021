from abc import ABC, abstractmethod


class SensorStrategy(ABC):
    @abstractmethod
    def read_sensor_values(self) -> dict:
        """
        Logic used by the SensorAgent to collect data from the environment.
        :return: an object containing the detected data
        """
        pass


class ActuatorStrategy(ABC):
    @abstractmethod
    def perform_action(self, behaviour) -> None:
        """
        Action that defines the logic used to activate the actuator
        :param behaviour: used to execute the actuator activation logic
        """
        pass


class SpreadingStrategy(ABC):
    @abstractmethod
    def spreading(self, behaviour, information: str) -> bool:
        """
        Action that defines the logic used for the spreading of information between the
        SensorAgent agents of the network
        :param behaviour: used to execute the spreading logic
        :param information: data to be spreaded
        :return: true if the spreading was successful, false otherwise
        """
        pass

