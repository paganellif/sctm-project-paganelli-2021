from spade.behaviour import CyclicBehaviour

from processing.triggerstrategy import TriggerStrategy
from processing.triggeragent import TriggerAgent
import util.config as cfg
import datetime


class TriggerStrategyImpl(TriggerStrategy):
    def __init__(self):
        self.num_event_detections = cfg.trigger_events["events_num"]
        self.delta_time = datetime.timedelta(seconds=cfg.trigger_events["period"])

    def check_event_detections(self, behaviour: CyclicBehaviour) -> bool:
        target: str = behaviour.agent.get("agent_jid")
        db_coll = cfg.collections["event_detections"]
        res = behaviour.agent.db_conn.select_last_detections(target, self.num_event_detections, db_coll)
        if res:
            if res.count(with_limit_and_skip=True) is self.num_event_detections:
                # To simplify the manipulation of timestamps, those obtained in the
                # result are converted, which are strings
                timestamps = list()
                for doc in res:
                    timestamps.append(doc["timestamp"])
                # The differences between the last NUM_EVENTS_DETECTIONS detections
                # are checked: if this difference is less than DELTA_TIME then these
                # detections are considered true and not spurious readings.
                i = 0
                true_event_detection = 0
                while i < (self.num_event_detections - 1):
                    tmp = (timestamps[i] - timestamps[i+1])

                    if cfg.logging["enabled"]:
                        behaviour.agent.log.log("Difference between two nearest event's timestamp: " + str(tmp))

                    if tmp < self.delta_time:
                        true_event_detection += 1

                    i += 1

                return true_event_detection is (self.num_event_detections - 1)
            else:
                return False
        else:
            return False


class FFDTriggerAgent(TriggerAgent):
    def __init__(self, agent_jid: str, password: str):
        super().__init__(agent_jid, password)
        self.check_strategy = TriggerStrategyImpl()
