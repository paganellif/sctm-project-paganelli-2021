from WSN.nodemanageragent import NodeManagerAgent
from WSN.nodemanagerstrategy import CheckConfigStrategy, GetConfigStrategy
import util.config as cfg
import psutil


class CheckConfigStrategyImpl(CheckConfigStrategy):

    def check_config(self, values: dict) -> bool:
        return True


class GetConfigStrategyImpl(GetConfigStrategy):

    def get_config(self):
        info: dict = dict()

        # CONFIG INFO
        info["config"] = dict()
        info["config"]["state"] = cfg.node["state"]
        info["config"]["name"] = cfg.node["name"]
        info["config"]["type"] = cfg.node["type"]
        info["config"]["spreading_param"] = cfg.spread["k_param"]
        info["config"]["logging"] = cfg.logging["enabled"]
        info["config"]["flame_samples"] = cfg.digital_input["sampling"]
        info["config"]["flame_debounce"] = cfg.digital_input["debounce"]
        info["config"]["trigger_events_num"] = cfg.trigger_events["events_num"]
        info["config"]["trigger_events_period"] = cfg.trigger_events["period"]
        info["config"]["alarm_total_duration"] = cfg.alarm["duration"]
        info["config"]["alarm_period"] = cfg.alarm["period"]
        info["config"]["neighbours"] = cfg.neighbours["jids"]

        # NODE INFO
        info["cpu"] = dict()
        freq = psutil.cpu_freq()
        info["cpu"]["cpu_freq_cur"] = freq[0]
        info["cpu"]["cpu_freq_min"] = freq[1]
        info["cpu"]["cpu_freq_max"] = freq[2]
        load = psutil.getloadavg()
        info["cpu"]["sys_avg_load_1"] = load[0]
        info["cpu"]["sys_avg_load_5"] = load[1]
        info["cpu"]["sys_avg_load_15"] = load[2]
        info["cpu"]["temp"] = psutil.sensors_temperatures()["cpu_thermal"][0][1]
        info["cpu"]["boot_time"] = psutil.boot_time()
        info["net"] = dict()
        if cfg.node["gateway"]:
            eth = psutil.net_io_counters(pernic=True)["eth0"]
            info["net"]["tot_bytes_eth_out"] = eth[0]
            info["net"]["tot_bytes_eth_in"] = eth[1]
            info["net"]["tot_pkt_dropped_out"] = eth[7]
            info["net"]["tot_pkt_dropped_in"] = eth[6]
            eth_stat = psutil.net_if_stats()["eth0"]
            info["net"]["eth_speed"] = eth_stat[2]
            info["net"]["eth_mtu"] = eth_stat[3]
            wlan_stat = psutil.net_if_stats()["wlan0"]
            info["net"]["wlan_isup"] = wlan_stat[0]
            info["net"]["wlan_speed"] = wlan_stat[2]
            info["net"]["wlan_mtu"] = wlan_stat[3]
            wlan = psutil.net_io_counters(pernic=True)["wlan0"]
            info["net"]["tot_bytes_wlan_out"] = wlan[0]
            info["net"]["tot_bytes_wlan_in"] = wlan[1]
        else:
            wlan_stat = psutil.net_if_stats()["wlan0"]
            info["net"]["wlan_speed"] = wlan_stat[2]
            info["net"]["wlan_mtu"] = wlan_stat[3]
            wlan = psutil.net_io_counters(pernic=True)["wlan0"]
            info["net"]["tot_bytes_wlan_out"] = wlan[0]
            info["net"]["tot_bytes_wlan_in"] = wlan[1]

        return info


class FFDNodeManagerAgent(NodeManagerAgent):
    def __init__(self, agent_jid: str, password: str):
        super().__init__(agent_jid, password)
        self.check_config_strategy = CheckConfigStrategyImpl()
        self.get_config_strategy = GetConfigStrategyImpl()
