"""Message bus abstraction: Kafka in production, an in-memory log in tests.

The live simulator and the matcher only talk to a ``Bus``. ``InMemoryBus``
keeps Kafka's semantics that matter here: topics split into partitions, keys
hashed to a partition, order kept within a partition, and consumers that start
from the beginning or the end. Messages are JSON-encoded on the way in and
decoded on the way out, so tests exercise the real serialization too.
"""
from __future__ import annotations

import zlib
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Protocol, Sequence, Tuple

from .schema import decode, encode


@dataclass
class Message:
    topic: str
    partition: int
    offset: int
    key: str
    value: dict
    replay: bool = False  # was already in the topic when the consumer started (history, not news)


class Producer(Protocol):
    def produce(self, topic: str, key: str, value: dict, partition: Optional[int] = None) -> None: ...

    def flush(self) -> None: ...


class Consumer(Protocol):
    def poll(self, timeout_s: float) -> List[Message]:
        """Next available messages (possibly none, after waiting up to timeout_s)."""

    def caught_up(self) -> bool:
        """Read everything that was in the topics when this consumer was created."""

    def close(self) -> None: ...


class Bus(Protocol):
    def partitions(self, topic: str) -> int: ...

    def producer(self) -> Producer: ...

    def consumer(self, topics: Sequence[str], from_beginning: bool, skip_types: Iterable[str] = ()) -> Consumer: ...


def partition_for(key: str, n: int) -> int:
    return zlib.crc32(key.encode()) % n


# ---------------------------------------------------------------- in-memory
class InMemoryBus:
    """Single-process bus. Delivery follows global produce order, which is one valid Kafka interleaving."""

    def __init__(self, partitions: int = 1):
        self.n_partitions = partitions
        self.log: List[Tuple[str, int, int, str, str, bytes]] = []  # topic, partition, offset, key, type, payload
        self._next_offset: Dict[Tuple[str, int], int] = {}

    def partitions(self, topic: str) -> int:
        return self.n_partitions

    def producer(self) -> "InMemoryBus":
        return self

    def produce(self, topic: str, key: str, value: dict, partition: Optional[int] = None) -> None:
        p = partition_for(key, self.n_partitions) if partition is None else partition
        offset = self._next_offset.get((topic, p), 0)
        self._next_offset[(topic, p)] = offset + 1
        self.log.append((topic, p, offset, key, value["type"], encode(value)))

    def flush(self) -> None:
        pass

    def consumer(self, topics: Sequence[str], from_beginning: bool, skip_types: Iterable[str] = ()) -> "InMemoryConsumer":
        return InMemoryConsumer(self, topics, from_beginning, skip_types)


class InMemoryConsumer:
    def __init__(self, bus: InMemoryBus, topics: Sequence[str], from_beginning: bool, skip_types: Iterable[str]):
        self.bus = bus
        self.topics = set(topics)
        self.skip = set(skip_types)
        self.pos = 0 if from_beginning else len(bus.log)
        self.target = len(bus.log)

    def poll(self, timeout_s: float = 0.0) -> List[Message]:
        out = []
        log = self.bus.log
        while self.pos < len(log):
            topic, p, offset, key, typ, payload = log[self.pos]
            replay = self.pos < self.target
            self.pos += 1
            if topic in self.topics and typ not in self.skip:
                out.append(Message(topic, p, offset, key, decode(payload), replay))
        return out

    def caught_up(self) -> bool:
        return self.pos >= self.target

    def close(self) -> None:
        pass
