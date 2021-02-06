import unittest
import util.config as cfg


class ConfigTestCase(unittest.TestCase):

    def test_node_config(self):
        self.assertIsNotNone(cfg.node["gateway"])
        self.assertIsNotNone(cfg.node["frontend"])
        self.assertIsNotNone(cfg.node["name"])

        self.assertIsInstance(cfg.node["gateway"], bool)
        self.assertIsInstance(cfg.node["frontend"], bool)
        self.assertIsInstance(cfg.node["name"], str)

        if cfg.node["gateway"]:
            self.assertIs(cfg.node["frontend"], False)
            self.assertIs("gateway" in cfg.node["name"], True)
        else:
            self.assertIs(cfg.node["frontend"], True)
            self.assertIs("frontend" in cfg.node["name"], True)

    def test_database_config(self):
        self.assertIsNotNone(cfg.database["db_name"])
        self.assertIsNotNone(cfg.database["hostname"])
        self.assertIsNotNone(cfg.database["username"])
        self.assertIsNotNone(cfg.database["password"])
        self.assertIsNotNone(cfg.database["url"])

        self.assertIsNotNone(cfg.collections["sensors_detections"])
        self.assertIsNotNone(cfg.collections["event_detections"])
        self.assertIsNotNone(cfg.collections["triggered_actions"])
        self.assertIsNotNone(cfg.collections["failure_reports"])
        self.assertIsNotNone(cfg.collections["detection_statistics"])

        self.assertIsInstance(cfg.database["db_name"], str)
        self.assertIsInstance(cfg.database["hostname"], str)
        self.assertIsInstance(cfg.database["username"], str)
        self.assertIsInstance(cfg.database["password"], str)
        self.assertIsInstance(cfg.database["url"], str)

        self.assertIsInstance(cfg.collections["sensors_detections"], str)
        self.assertIsInstance(cfg.collections["event_detections"], str)
        self.assertIsInstance(cfg.collections["triggered_actions"], str)
        self.assertIsInstance(cfg.collections["failure_reports"], str)
        self.assertIsInstance(cfg.collections["detection_statistics"], str)

    def test_environmental_parameters_config(self):
        self.assertIsNotNone(cfg.trigger_events["event"])
        self.assertIsNotNone(cfg.trigger_events["events_num"])
        self.assertIsNotNone(cfg.trigger_events["period"])
        self.assertIsNotNone(cfg.parameters["temperature"])
        self.assertIsNotNone(cfg.parameters["humidity"])
        self.assertIsNotNone(cfg.parameters["smoke"])

        self.assertIsInstance(cfg.trigger_events["event"], str)
        self.assertIsInstance(cfg.trigger_events["events_num"], int)
        self.assertIsInstance(cfg.trigger_events["period"], int)
        self.assertIsInstance(cfg.parameters["temperature"], str)
        self.assertIsInstance(cfg.parameters["humidity"], str)
        self.assertIsInstance(cfg.parameters["smoke"], str)

        self.assertIs(cfg.trigger_events["events_num"] > 0, True)
        self.assertIs(cfg.trigger_events["period"] > 0, True)

        self.assertIs(cfg.trigger_events["event"] not in cfg.parameters, True)

    def test_xmpp_config(self):
        self.assertIsNotNone(cfg.xmpp["hostname"])
        self.assertIsNotNone(cfg.xmpp["port"])
        self.assertIsNotNone(cfg.jid["trigger_agent"])
        self.assertIsNotNone(cfg.jid["dbmanager_agent"])
        self.assertIsNotNone(cfg.jid["statistics_agent"])
        self.assertIsNotNone(cfg.jid["frontend_agent"])
        self.assertIsNotNone(cfg.jid["sensor_agent"])
        self.assertIsNotNone(cfg.jid["nodemanager_agent"])

        self.assertIsInstance(cfg.xmpp["hostname"], str)
        self.assertIsInstance(cfg.xmpp["port"], int)
        self.assertIsInstance(cfg.jid["trigger_agent"], str)
        self.assertIsInstance(cfg.jid["dbmanager_agent"], str)
        self.assertIsInstance(cfg.jid["statistics_agent"], str)
        self.assertIsInstance(cfg.jid["frontend_agent"], str)
        self.assertIsInstance(cfg.jid["sensor_agent"], str)
        self.assertIsInstance(cfg.jid["nodemanager_agent"], str)

        for jid in cfg.jid:
            self.assertIs(str("@c"+cfg.xmpp["hostname"]) in jid, True)

    def test_sensor_config(self):
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

        self.assertIsNotNone(cfg.digital_input["sampling"])
        self.assertIsInstance(cfg.digital_input["sampling"], int)
        self.assertIs(cfg.digital_input["sampling"] > 0, True)

        self.assertIsNotNone(cfg.alarm["duration"])
        self.assertIsNotNone(cfg.alarm["period"])

        self.assertIsInstance(cfg.alarm["duration"], int)
        self.assertIsInstance(cfg.alarm["period"], int)

    def test_spreading_config(self):
        None
        # TODO: TBC

    def test_logging_config(self):
        self.assertIsNotNone(cfg.logging["enabled"])
        self.assertIsNotNone(cfg.logging["level"])

        self.assertIsInstance(cfg.logging["enabled"], bool)
        self.assertIsInstance(cfg.logging["level"], bool)

        self.assertIs(cfg.logging["level"] in ["INFO", "DEBUG"], True)

    def test_frontend_config(self):
        self.assertIsNotNone(cfg.web["hostname"])
        self.assertIsNotNone(cfg.web["port"])

        self.assertIsInstance(cfg.web["hostname"], str)
        self.assertIsInstance(cfg.web["port"], int)

        self.assertIs(cfg.web["hostname"] is cfg.xmpp["hostname"], True)
        self.assertIs(cfg.web["port"] is not cfg.xmpp["port"], True)
