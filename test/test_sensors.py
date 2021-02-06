import unittest
import RPi.GPIO as GPIO
import util.config as cfg
import dht11


class SensorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

    def test_pin_setup(self):
        self.assertIsNotNone(cfg.pin["dht11"])
        self.assertIsInstance(cfg.pin["dht11"], int)

        self.assertIsNotNone(cfg.pin["mq2"])
        self.assertIsInstance(cfg.pin["mq2"], str)  # analog input

        self.assertIsNotNone(cfg.pin["button"])
        self.assertIsInstance(cfg.pin["button"], int)

        self.assertIsNotNone(cfg.pin["buzzer"])
        self.assertIsInstance(cfg.pin["buzzer"], int)

        self.assertIsNotNone(cfg.pin["red_led"])
        self.assertIsInstance(cfg.pin["red_led"], int)

        self.assertIsNotNone(cfg.pin["yellow_led"])
        self.assertIsInstance(cfg.pin["yellow_led"], int)

        self.assertIsNotNone(cfg.pin["green_led"])
        self.assertIsInstance(cfg.pin["green_led"], int)

    def test_temperature(self):
        sensor = dht11.DHT11(pin=cfg.pin["dht11"])
        attempts = 20
        result = False

        self.assertIsNotNone(sensor)

        read = sensor.read()
        self.assertIsNotNone(read)

        if read.is_valid():
            self.assertIsNotNone(read.temperature)
            self.assertIsInstance(read.temperature, int, float)

        for i in range(0, attempts):
            result |= sensor.read().is_valid()

        self.assertIs(result, True)

    def test_humidity(self):
        sensor = dht11.DHT11(pin=cfg.pin["dht11"])
        attempts = 20
        result = False

        self.assertIsNotNone(sensor)

        read = sensor.read()
        self.assertIsNotNone(read)

        if read.is_valid():
            self.assertIsNotNone(read.humidity)
            self.assertIsInstance(read.humidity, int, float)

        for i in range(0, attempts):
            result |= sensor.read().is_valid()

        self.assertIs(result, True)

    def test_smoke(self):
        None
        # TODO: TBC


