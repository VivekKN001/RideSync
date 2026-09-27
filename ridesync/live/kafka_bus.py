"""``Bus`` on Apache Kafka via confluent-kafka (librdkafka).

- Producer: idempotent (no duplicates from its own retries), lz4.
- Tuned for latency, not throughput: no linger (messages go out at once; librdkafka still
  batches whatever queues up while a request is in flight), Nagle off, and the broker
  answers an empty fetch after 10 ms instead of 500 ms.
- ``prefix`` namespaces every topic (tests use their own topics and never touch real runs).
- Consumers use manual partition assignment and never commit offsets: the
  simulator starts at the end of its input topics, and the matcher starts at the
  beginning and rebuilds its state (see ``ridesync.live.matcher``).
"""
from __future__ import annotations

import time
import uuid
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .bus import Message
from .schema import decode, encode


class KafkaBus:
    def __init__(self, bootstrap: str = "localhost:9092", prefix: str = ""):
        from confluent_kafka.admin import AdminClient

        self.bootstrap = bootstrap
        self.prefix = prefix
        self._admin = AdminClient({"bootstrap.servers": bootstrap})
        self._partitions: Dict[str, int] = {}

    def partitions(self, topic: str) -> int:
        if topic not in self._partitions:
            name = self.prefix + topic
            meta = self._admin.list_topics(name, timeout=10).topics.get(name)
            if meta is None or meta.error is not None or not meta.partitions:
                raise RuntimeError(f"Kafka topic {name!r} is missing: run `python -m ridesync.live.topics`")
            self._partitions[topic] = len(meta.partitions)
        return self._partitions[topic]

    def producer(self) -> "KafkaProducer":
        return KafkaProducer(self.bootstrap, self.prefix)

    def consumer(self, topics: Sequence[str], from_beginning: bool, skip_types: Iterable[str] = ()) -> "KafkaConsumer":
        return KafkaConsumer(self, topics, from_beginning, skip_types)


class KafkaProducer:
    def __init__(self, bootstrap: str, prefix: str = ""):
        from confluent_kafka import Producer

        self.prefix = prefix
        self._p = Producer({
            "bootstrap.servers": bootstrap,
            "enable.idempotence": True,
            "compression.type": "lz4",
            "linger.ms": 0,
            "socket.nagle.disable": True,
        })

    def produce(self, topic: str, key: str, value: dict, partition: Optional[int] = None) -> None:
        kwargs = {} if partition is None else {"partition": partition}
        while True:
            try:
                self._p.produce(self.prefix + topic, value=encode(value), key=key.encode(),
                                headers=[("type", value["type"].encode())], **kwargs)
                break
            except BufferError:  # local queue full: let deliveries drain, then retry
                self._p.poll(0.05)
        self._p.poll(0)

    def flush(self, timeout_s: float = 30.0) -> None:
        left = self._p.flush(timeout_s)
        if left:
            raise RuntimeError(f"{left} Kafka messages still undelivered after {timeout_s}s")


class KafkaConsumer:
    def __init__(self, bus: KafkaBus, topics: Sequence[str], from_beginning: bool, skip_types: Iterable[str]):
        from confluent_kafka import OFFSET_BEGINNING, OFFSET_END, Consumer, TopicPartition

        self._c = Consumer({
            "bootstrap.servers": bus.bootstrap,
            "group.id": f"ridesync-{uuid.uuid4().hex[:8]}",  # required by librdkafka; offsets are never committed
            "enable.auto.commit": False,
            "fetch.wait.max.ms": 10,
            "socket.nagle.disable": True,
        })
        self.prefix = bus.prefix
        start = OFFSET_BEGINNING if from_beginning else OFFSET_END
        tps = [TopicPartition(bus.prefix + t, p, start) for t in topics for p in range(bus.partitions(t))]
        # Catch-up target: the log end of every partition at creation time.
        self._targets: Dict[Tuple[str, int], int] = {}
        if from_beginning:
            for tp in tps:
                lo, hi = self._log_range(TopicPartition(tp.topic, tp.partition))
                if hi > lo:
                    self._targets[(tp.topic, tp.partition)] = hi
        self._ends = dict(self._targets)
        self._c.assign(tps)
        self.skip = {s.encode() for s in skip_types}

    def _log_range(self, tp, attempts: int = 50) -> Tuple[int, int]:
        """(low, high) offsets. Retries while a just-created partition's leader is still being elected."""
        from confluent_kafka import KafkaError, KafkaException

        electing = {KafkaError.NOT_LEADER_FOR_PARTITION, KafkaError.LEADER_NOT_AVAILABLE,
                    KafkaError.UNKNOWN_TOPIC_OR_PART}
        for attempt in range(attempts):
            try:
                return self._c.get_watermark_offsets(tp, timeout=10)
            except KafkaException as e:
                err = e.args[0]
                if not (err.retriable() or err.code() in electing) or attempt == attempts - 1:
                    raise
                time.sleep(0.2)
        raise AssertionError("unreachable")

    def poll(self, timeout_s: float) -> List[Message]:
        from confluent_kafka import KafkaError, KafkaException

        # consume() waits out its whole timeout unless the batch fills up, so block on the first
        # message with poll() (returns as soon as one arrives), then drain what's already queued.
        first = self._c.poll(timeout_s)
        if first is None:
            return []
        out = []
        for m in [first] + self._c.consume(num_messages=2000, timeout=0):
            err = m.error()
            if err is not None:
                if err.code() == KafkaError._PARTITION_EOF:
                    continue
                raise KafkaException(err)
            tp = (m.topic(), m.partition())
            replay = m.offset() < self._ends.get(tp, 0)
            if tp in self._targets and m.offset() + 1 >= self._targets[tp]:
                del self._targets[tp]
            if self.skip:
                typ = next((v for k, v in (m.headers() or ()) if k == "type"), None)
                if typ in self.skip:
                    continue
            out.append(Message(m.topic()[len(self.prefix):], m.partition(), m.offset(), (m.key() or b"").decode(),
                               decode(m.value()), replay))
        return out

    def caught_up(self) -> bool:
        return not self._targets

    def close(self) -> None:
        self._c.close()
