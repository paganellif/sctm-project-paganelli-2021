env = dict()
env["development"] = True

######################################################################
# Node Configuration
######################################################################
# Node Information
node = dict()
node["gateway"] = False  # True if this node is the gateway, False if this node is an end-device
node["frontend"] = True  # True if this node is the frontend, False otherwise
node["router"] = False  # True if this node is a router, False otherwise

if node["frontend"]:
    node["type"] = "Front-end"
elif node["gateway"]:
    node["name"] = "gateway.rpi1"
    node["type"] = "Gateway"
else:
    if node["router"]:
        node["type"] = "Router"
        node["name"] = "router.rpi10"  # router.rpi3, router.rpi4, ....
    else:
        node["type"] = "End-Device"
        node["name"] = "edge.rpi2"  # end.rpi3, end.rpi4, ....

node["state"] = "RUNNING"

######################################################################
# Database Configuration
######################################################################
# Database credentials
database = dict()
if env["development"]:
    database["db_name"] = "testdb"
else:
    database["db_name"] = "wsn-ffd"
database["hostname"] = "***********"
database["dbmanger_user"] = "dbmanager1"
database["dbmanager_pwd"] = "***********"
database["dbmanager_url"] = "mongodb+srv://" + database["dbmanger_user"] + ":" + database["dbmanager_pwd"] + "@" +\
                            database["hostname"] + "/" + database["db_name"] + "?retryWrites=true&w=majority"

database["frontend_user"] = "frontend"
database["frontend_pwd"] = "***********"
database["frontend_url"] = "mongodb+srv://" + database["frontend_user"] + ":" + database["frontend_pwd"] + "@" +\
                            database["hostname"] + "/" + database["db_name"] + "?retryWrites=true&w=majority"

database["statistics_user"] = "statistics"
database["statistics_pwd"] = "***********"
database["statistics_url"] = "mongodb+srv://" + database["statistics_user"] + ":" + database["statistics_pwd"] + "@" +\
                            database["hostname"] + "/" + database["db_name"] + "?retryWrites=true&w=majority"

database["trigger_user"] = "trigger"
database["trigger_pwd"] = "***********"
database["trigger_url"] = "mongodb+srv://" + database["trigger_user"] + ":" + database["trigger_pwd"] + "@" +\
                            database["hostname"] + "/" + database["db_name"] + "?retryWrites=true&w=majority"

# Collections names
collections = dict()
collections["sensors_detections"] = "sensors_detections"
collections["event_detections"] = "event_detections"
collections["triggered_actions"] = "triggered_actions"
collections["failure_reports"] = "failure_reports"
collections["detection_statistics"] = "detection_statistics"
collections["nodes_configs"] = "nodes_configs"

# Trigger event - Core environmental parameter
trigger_events = dict()
trigger_events["event"] = "flame"
trigger_events["events_num"] = 2
trigger_events["period"] = 10

# Other environmental parameters
parameters = dict()
parameters["temperature"] = "temp"
parameters["humidity"] = "hum"
parameters["smoke"] = "smoke"

######################################################################
# XMPP Configuration
######################################################################
# XMPP credentials
xmpp = dict()
xmpp["hostname"] = "***********"
xmpp["port"] = 5222

# Jabber ids of sink agents
jid = dict()
jid["trigger_agent"] = "trigger@" + xmpp["hostname"]
jid["dbmanager_agent"] = "dbmanager@" + xmpp["hostname"]
jid["statistics_agent"] = "statistics@" + xmpp["hostname"]
jid["frontend_agent"] = "frontend@" + xmpp["hostname"]
if not node["frontend"]:
    jid["sensor_agent"] = "sensor." + node["name"] + "@" + xmpp["hostname"]
    jid["nodemanager_agent"] = "nodemanager." + node["name"] + "@" + xmpp["hostname"]

# jid["test_sensor_agent"] = "TESTsensor." + node["name"] + "@" + xmpp["hostname"]

######################################################################
# Sensor Configuration
######################################################################
# RPiO configuration
gpio = dict()
gpio["mode"] = "BCM"

sensor_type = dict()
sensor_type["dht"] = 11
sensor_type["mq"] = 2

# button parameters configuration
digital_input = dict()
digital_input["sampling"] = 4
digital_input["debounce"] = None

# pin configuration
pin = dict()
pin["dht"] = 4
pin["mq"] = 0  # equals to A0
pin["button"] = 14
pin["buzzer"] = 23
pin["red_led"] = 21
pin["yellow_led"] = 20
pin["green_led"] = 16

# buzzer/alarm configuration
alarm = dict()
# a duration of 20 and a period of 2 means that the alarm is switched on/off 10 times where every state (on/off) has a
# period of 2 seconds
alarm["duration"] = 10  # duration of alarm activation in seconds
alarm["period"] = 1  # number of cycle performed

######################################################################
# Spreading Configuration
######################################################################
# spreading K parameter configuration
spread = dict()
spread["k_param"] = 0

# neighbours configuration
neighbours = dict()
neighbours["jids"] = []
if not node["frontend"] and not node["gateway"]:
    neighbours["jids"].append("sensor.gateway@" + xmpp["hostname"])
    # neighbours["jids"].append("sensor.edge.RPi3@" + xmpp["hostname"])
    # , ...
elif not node["frontend"] and node["gateway"]:
    var = None
    # neighbours["jids"].append("sensor.edge.RPi3@" + xmpp["hostname"])
    # , ...


######################################################################
# Logging Configuration
######################################################################
# Logger configuration
logging = dict()
logging["enabled"] = True
logging["level"] = "INFO"

######################################################################
# FrontEnd Configuration
######################################################################
web = dict()
web["hostname"] = "0.0.0.0"
web["port"] = 8080
