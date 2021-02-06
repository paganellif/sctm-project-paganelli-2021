from spade.behaviour import FSMBehaviour
from aioxmpp import JID
import util.config as cfg


class BaseFSM(FSMBehaviour):
    def on_subscribe(self, agent_jid: str) -> None:
        if JID.fromstr(agent_jid) in self.agent.presence.get_contacts():
            if cfg.logging["enabled"]:
                self.agent.log.log("Agent " + agent_jid + " is already in the contact list")
        else:
            if cfg.logging["enabled"]:
                self.agent.log.log("Subscription request from " + agent_jid + " approved")

            self.presence.approve(agent_jid)
            self.presence.subscribe(agent_jid)

    def on_subscribed(self, agent_jid: str) -> None:
        if cfg.logging["enabled"]:
            self.agent.log.log("Agent " + agent_jid + " has accepted the subscription")

    def on_unsubscribe(self, agent_jid: str) -> None:
        if JID.fromstr(agent_jid) in self.agent.presence.get_contacts():
            if cfg.logging["enabled"]:
                self.agent.log.log("Unsubscription request from " + agent_jid + " accepted")

            self.presence.approve(agent_jid)

    def on_unsubscribed(self, agent_jid: str) -> None:
        if cfg.logging["enabled"]:
            self.agent.log.log("Agent " + agent_jid + " has accepted the unsubscription")

    def on_available(self, agent_jid: str, stanza) -> None:
        if cfg.logging["enabled"]:
            self.agent.log.log("Agent " + agent_jid + " is available")

    def on_unavailable(self, agent_jid: str, stanza) -> None:
        if cfg.logging["enabled"]:
            self.agent.log.log("Agent " + agent_jid + " is unavailable")

    async def on_start(self):
        self.presence.on_subscribe = self.on_subscribe
        self.presence.on_subscribed = self.on_subscribed
        self.presence.on_unsubscribe = self.on_unsubscribe
        self.presence.on_unsubscribed = self.on_unsubscribed
        self.presence.on_available = self.on_available
        self.presence.on_unavailable = self.on_unavailable
        self.presence.set_available()
        # TODO self.presence.approve_all = True
