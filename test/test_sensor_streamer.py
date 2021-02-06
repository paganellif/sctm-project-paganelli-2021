from WSN.sensorstreamerfactory import FFDSensorStreamer, SensorStreamerFactory
import unittest


class StreamerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = SensorStreamerFactory()

    def test_create_sensor_streamer(self):
        sensor_streamer = self.factory.create_sensor_streamer()
        self.assertIsNotNone(sensor_streamer)
        self.assertIsInstance(sensor_streamer, FFDSensorStreamer)

    def test_get_temp(self):
        sensor_streamer = self.factory.create_sensor_streamer()
        temp = sensor_streamer.get_temp()
        self.assertIsNotNone(temp)
        self.assertIsInstance(temp, float)

    def test_get_hum(self):
        sensor_streamer = self.factory.create_sensor_streamer()
        hum = sensor_streamer.get_hum()
        self.assertIsNotNone(hum)
        self.assertIsInstance(hum, float)

    def test_get_smoke(self):
        sensor_streamer = self.factory.create_sensor_streamer()
        smoke = sensor_streamer.get_smoke()
        self.assertIsNotNone(smoke)
        self.assertIsInstance(smoke, float)

    def test_get_flame(self):
        sensor_streamer = self.factory.create_sensor_streamer()
        flame = sensor_streamer.get_flame()
        self.assertIsNotNone(flame)
        self.assertIsInstance(flame, bool)
