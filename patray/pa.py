from dataclasses import dataclass, field
from enum import Enum
from itertools import chain
from typing import List, Optional, TypeVar

from loguru import logger
from pulsectl import Pulse as PulseOriginal
from pulsectl import PulseCardInfo, PulseCardProfileInfo, PulsePortInfo, PulseSinkInfo, PulseSourceInfo


@dataclass
class CardProfile:
    id: int
    card_id: int
    name: str
    sinks_count: int
    sources_count: int
    original: PulseCardProfileInfo = field(repr=False)

    @classmethod
    def from_pa_card_profile(cls, id: int, card_id: int, pa_card_profile: PulseCardProfileInfo):
        return cls(
            id=id,
            card_id=card_id,
            name=pa_card_profile.description,
            sinks_count=pa_card_profile.n_sinks,
            sources_count=pa_card_profile.n_sources,
            original=pa_card_profile,
        )


@dataclass
class Card:
    id: int
    name: str
    active_profile_id: Optional[int]
    profiles: List[CardProfile]
    original: PulseCardInfo = field(repr=False)

    @classmethod
    def from_pa_card(cls, id: int, pa_card: PulseCardInfo):
        profiles = []
        active_id = None
        for i, profile in enumerate(pa_card.profile_list):
            profiles.append(CardProfile.from_pa_card_profile(id=i, card_id=id, pa_card_profile=profile))
            if profile.name == pa_card.profile_active.name:
                active_id = i
        return cls(
            id=id,
            name=pa_card.proplist["device.description"],
            active_profile_id=active_id,
            profiles=profiles,
            original=pa_card,
        )


@dataclass
class Port:
    id: int
    end_id: int
    name: str
    original: PulsePortInfo = field(repr=False)

    @classmethod
    def from_pa_port(cls, id: int, end_id: int, pa_port: PulsePortInfo):
        return cls(
            id=id,
            end_id=end_id,
            name=pa_port.description,
            original=pa_port,
        )


EndOriginalType = TypeVar("EndOriginalType", PulseSinkInfo, PulseSourceInfo)


class EndType(Enum):
    sink = PulseSinkInfo
    source = PulseSourceInfo

    @classmethod
    def from_instance(cls, instance: EndOriginalType):
        return cls(type(instance))


@dataclass
class End:
    id: int
    type: EndType
    name: str
    volume: float
    active_port_id: Optional[int]
    ports: List[Port]
    original: EndOriginalType = field(repr=False)

    @classmethod
    def from_pa_end(cls, id: int, pa_end: EndOriginalType):
        ports = []
        active_id = None
        for i, port in enumerate(pa_end.port_list):
            ports.append(Port.from_pa_port(id=i, end_id=id, pa_port=port))
            if port.name == pa_end.port_active.name:
                active_id = i
        return cls(
            id=id,
            type=EndType.from_instance(pa_end),
            name=pa_end.description,
            volume=pa_end.volume.value_flat,
            active_port_id=active_id,
            ports=ports,
            original=pa_end,
        )


class Pulse:

    def __init__(self, config):
        self.config = config
        self.pa = PulseOriginal("patray")

    def close(self):
        self.pa.close()

    def update(self):
        logger.debug("update called")
        self.cards = [Card.from_pa_card(id=i, pa_card=c) for i, c in enumerate(self.pa.card_list())]
        ends = chain(self.pa.sink_list(), self.pa.source_list())
        self.ends = [End.from_pa_end(id=i, pa_end=e) for i, e in enumerate(ends)]

    def set_profile(self, profile: CardProfile):
        card = self.cards[profile.card_id]
        self.pa.card_profile_set(card.original, profile.original)
        logger.info("set profile {!r} on card {!r}", profile.name, card.name)

    def set_port(self, port: Port):
        end = self.ends[port.end_id]
        self.pa.port_set(end.original, port.original)
        logger.info("set port {!r} on end {!r}", port.name, end.name)

    def set_volume(self, end: End, volume: float):
        self.pa.volume_set_all_chans(end.original, volume)
        logger.info("set volume {} on end {!r}", volume, end.name)
