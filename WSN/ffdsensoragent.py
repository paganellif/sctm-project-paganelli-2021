import datetime
import random
import uuid
from aioxmpp import JID
from WSN.sensoragent import SensorAgent
from WSN.sensorstrategy import SensorStrategy, ActuatorStrategy, SpreadingStrategy
from WSN.sensorstreamerfactory import SensorStreamerFactory
from spade.message import Message
import util.config as cfg
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
import RPi.GPIO as GPIO


class SensorStrategyImpl(SensorStrategy):
    def __init__(self):
        self.__sensor_streamer = SensorStreamerFactory().create_sensor_streamer()
        GPIO.setup(cfg.pin["buzzer"], GPIO.OUT)

    def read_sensor_values(self) -> dict:
        temp = self.__sensor_streamer.get_temp()
        hum = self.__sensor_streamer.get_hum()
        smoke = self.__sensor_streamer.get_smoke()
        flame = self.__sensor_streamer.get_flame()
        return {cfg.parameters["temperature"]: temp,
                cfg.parameters["humidity"]: hum,
                cfg.parameters["smoke"]: smoke,
                cfg.trigger_events["event"]: flame}


class ActuatorStrategyImpl(ActuatorStrategy):
    class ActionBehav(PeriodicBehaviour):
        def __init__(self, period, duration):
            super().__init__(period)
            self.start_time = datetime.datetime.now()
            self.end_time = self.start_time + datetime.timedelta(seconds=duration)

        async def on_start(self):
            msg = Message(to=cfg.jid["nodemanager_agent"])
            msg.set_metadata("performative", "inform")
            msg.body = "ALARM ON"
            await self.send(msg)

            if cfg.logging["enabled"]:
                self.agent.log.log("ACTION STARTED!")

        async def run(self):
            if self.agent.alarm_state is True:
                # BUZZER ON
                GPIO.output(cfg.pin["buzzer"], GPIO.LOW)
                self.agent.alarm_state = False
            else:
                # BUZZER OFF
                GPIO.output(cfg.pin["buzzer"], GPIO.HIGH)
                self.agent.alarm_state = True

            if cfg.logging["enabled"]:
                self.agent.log.log("ACTION RUNNING")
                self.agent.log.log("ALARM ON!")

            if datetime.datetime.now() >= self.end_time:
                msg = Message(to=cfg.jid["trigger_agent"])
                msg.set_metadata("performative", "inform")
                msg.body = "Job done!"
                await self.send(msg)
                self.kill()
                return

        async def on_end(self):
            self.agent.remove_behaviour(self)
            msg = Message(to=cfg.jid["nodemanager_agent"])
            msg.set_metadata("performative", "inform")
            msg.body = "RUNNING"
            await self.send(msg)

            # BUZZER OFF
            GPIO.output(cfg.pin["buzzer"], GPIO.LOW)
            self.agent.alarm_state = False

            if cfg.logging["enabled"]:
                self.agent.log.log("ACTION ENDED!")

    def perform_action(self, behaviour: CyclicBehaviour) -> None:
        behaviour.agent.add_behaviour(self.ActionBehav(period=cfg.alarm["period"], duration=cfg.alarm["duration"]))


class SpreadingStrategyImpl(SpreadingStrategy):
    async def __perform_spreading(self, behaviour):
        contact_list: list = list(behaviour.agent.presence.get_contacts().keys()).copy()
        contact_list.remove(JID.fromstr(cfg.jid["dbmanager_agent"]))
        contact_list.remove(JID.fromstr(cfg.jid["trigger_agent"]))
        contact_list.remove(JID.fromstr(cfg.jid["statistics_agent"]))

        if (behaviour.agent.spread_param >= len(contact_list)) or (behaviour.agent.spread_param == -1):
            real_contact_list = contact_list
        else:
            real_contact_list = random.choices(contact_list, k=behaviour.agent.spread_param)
        for agent in real_contact_list:
            if cfg.logging["enabled"]:
                behaviour.agent.log.log(str(agent))
                behaviour.agent.log.log(behaviour.agent.get("spreading_info_snd"))
            msg = Message(to=str(agent))
            msg.set_metadata("performative", "propagate")
            msg.body = behaviour.agent.get("spreading_info_snd")
            await behaviour.send(msg)

    async def spreading(self, behaviour, information: str) -> bool:
        behaviour.agent.set("spreading_info_rcv", information)

        if behaviour.agent.spread_param is 0:
            # There is no spreading of information
            return False
        # That means this is the FFDSensorAgent who start the spreading
        # because it's entered the spreading state without having received a message
        if behaviour.agent.get("spreading_info_rcv") is "":
            # Set the information that has to be spread
            msg_uid = "["+str(uuid.uuid1())+"] "
            behaviour.agent.set("spreading_info_snd", msg_uid+str(behaviour.agent.jid) + " triggered the alarm")
            await self.__perform_spreading(behaviour)
            # False means that the FFDSensorAgent has not to perform any action
            return False
        else:
            if behaviour.agent.get("spreading_info_rcv") == behaviour.agent.get("spreading_info_snd"):
                if cfg.logging["enabled"]:
                    behaviour.agent.log.log("Information received already disseminated")
                # False means that the FFDSensorAgent has not to perform any action
                return False
            else:
                # Set the information sent equal to the information received in order to
                # avoid the second message sending
                behaviour.agent.set("spreading_info_snd", behaviour.agent.get("spreading_info_rcv"))
                await self.__perform_spreading(behaviour)
                # True means that the FFDSensorAgent must perform the action on th actuator
                return True


class FFDSensorAgent(SensorAgent):
    def __init__(self, agent_jid: str, password: str, spread_param=2):
        if spread_param < -1:
            spread_param = 0
        super().__init__(agent_jid, password, spread_param=spread_param)
        self.sensor_read_strategy = SensorStrategyImpl()
        self.actuator_strategy = ActuatorStrategyImpl()
        self.spreading_strategy = SpreadingStrategyImpl()
        self.alarm_state = False
