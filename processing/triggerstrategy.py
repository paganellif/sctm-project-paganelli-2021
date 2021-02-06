from abc import ABC, abstractmethod


class TriggerStrategy(ABC):
    @abstractmethod
    def check_event_detections(self, behaviour) -> bool:
        """
        Checks the detections made by agents to determine their correctness
        :param behaviour: behavior that carries out the verification of the correctness of the detections
        :return: true if the detections made are correct, otherwise false
        """
        pass
