import pymongo
import util.config as cfg

if not cfg.node["frontend"]:
    import RPi.GPIO as GPIO
    from WSN.ffdsensoragent import FFDSensorAgent
    from WSN.ffdnodemanageragent import FFDNodeManagerAgent
    from processing.ffddbmanageragent import FFDDBManagerAgent
    from processing.ffdtriggeragent import FFDTriggerAgent
else:
    from presentation.frontendagent import FrontEndAgent
    from processing.statisticsagent import StatisticsAgent


def main():
    if not cfg.node["frontend"]:
        # Board Initialization
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(cfg.pin["red_led"], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(cfg.pin["yellow_led"], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(cfg.pin["green_led"], GPIO.OUT, initial=GPIO.LOW)

    # Database Initialization
    if cfg.node["gateway"]:
        client = pymongo.MongoClient(cfg.database["dbmanager_url"])
        if cfg.database["db_name"] not in client.list_database_names():
            if cfg.logging["enabled"]:
                print("Created database " + cfg.database["db_name"])

            for collection in cfg.collections.values():
                if cfg.logging["enabled"]:
                    print("Created collection " + collection)

                client[cfg.database["db_name"]].create_collection(collection)
        client.close()

    # Agent System Initialization
    if cfg.node["gateway"]:
        db_manager = FFDDBManagerAgent("dbmanager@"+cfg.xmpp["hostname"], "qwertyqwerty")
        db_manager.start(auto_register=True).result()

        trigger = FFDTriggerAgent("trigger@"+cfg.xmpp["hostname"], "qwertyqwerty")
        trigger.start(auto_register=True).result()

    if cfg.node["frontend"]:
        # this agent is running in the cloud
        frontend = FrontEndAgent("frontend@"+cfg.xmpp["hostname"], "qwertyqwerty")
        frontend.start(auto_register=True).result()

        # this agent is running in the cloud
        statistics = StatisticsAgent("statistics@"+cfg.xmpp["hostname"], "qwertyqwerty")
        statistics.start(auto_register=True).result()
    else:
        node_manager = FFDNodeManagerAgent(cfg.jid["nodemanager_agent"], "PASSWORD")
        node_manager.start(auto_register=True)

        # a sensor agent and a node manager agent must run in every node
        station = FFDSensorAgent(cfg.jid["sensor_agent"], "PASSWORD", cfg.spread["k_param"])
        station.start(auto_register=True)


if __name__ == '__main__':
    main()
