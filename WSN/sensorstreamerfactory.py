from abc import ABC, abstractmethod
import Adafruit_DHT
import util.config as cfg
import RPi.GPIO as GPIO
from math import nan
from gas_detection import GasDetection


class SensorStreamer(ABC):
    """

    """
    pass


class FFDSensorStreamer(SensorStreamer):
    def __init__(self):
        """
        Creates an FFDSensorStreamer.
        """
        self.__mq2 = GasDetection()
        self.__mq2.calibrate()
        GPIO.setup(cfg.pin["button"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def get_temp(self):
        """

        :return float: the temperature value read by the sensor DTH-11.
        """
        hum, temp = Adafruit_DHT.read_retry(cfg.sensor_type["dht"], cfg.pin["dht"])
        return temp if ((temp != 0.0) and (hum != 0.0)) else nan

    def get_hum(self):
        """

        :return float: the humidity value read by the sensor DTH-11.
        """
        hum, temp = Adafruit_DHT.read_retry(cfg.sensor_type["dht"], cfg.pin["dht"])
        return hum if ((temp != 0.0) and (hum != 0.0)) else nan

    def get_smoke(self):
        """
        :return boolean: the smoke gas value read by the sensor MQ-2.
        """
        return self.__mq2.percentage()[self.__mq2.SMOKE_GAS]

    def get_flame(self):
        """
        :return boolean: the flame value read by the sensor (simulated digital reading with push button).
        """
        result = False
        for i in range(cfg.digital_input["sampling"]):
            if GPIO.input(cfg.pin["button"]) is GPIO.LOW:
                result = True
        return result


class SensorStreamerAbstractFactory(ABC):
    @abstractmethod
    def create_sensor_streamer(self) -> SensorStreamer:
        """

        :return SensorStreamer: a new SensorStreamer
        """
        pass


class SensorStreamerFactory(SensorStreamerAbstractFactory):
    def create_sensor_streamer(self) -> FFDSensorStreamer:
        """
        :return FFDSensorStreamer: a new FFDSensorStreamer
        """
        return FFDSensorStreamer()
