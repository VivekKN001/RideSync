"""Create (or recreate) the RideSync Kafka topics.

    python -m ridesync.live.topics [--partitions 3] [--recreate]

The simulator and matcher call ``ensure_topics`` on start, so this is only
needed to change the partition count or wipe old runs.
"""
from __future__ import annotations

import argparse
import time

from .schema import ALL_TOPICS

RETENTION_MS = 6 * 3600 * 1000  # the matcher replays retained history on start, so keep it short


def ensure_topics(bootstrap: str, partitions: int = 3, recreate: bool = False, prefix: str = "") -> None:
    from confluent_kafka import KafkaError, KafkaException
    from confluent_kafka.admin import AdminClient, NewTopic

    admin = AdminClient({"bootstrap.servers": bootstrap})
    names = [prefix + t for t in ALL_TOPICS]
    if recreate:
        existing = set(admin.list_topics(timeout=10).topics) & set(names)
        if existing:
            for f in admin.delete_topics(sorted(existing)).values():
                f.result()
            while set(admin.list_topics(timeout=10).topics) & existing:  # deletion is asynchronous
                time.sleep(0.2)
    missing = [t for t in names if t not in admin.list_topics(timeout=10).topics]
    if not missing:
        return
    futures = admin.create_topics([
        NewTopic(t, num_partitions=partitions, replication_factor=1, config={"retention.ms": str(RETENTION_MS)})
        for t in missing
    ])
    for f in futures.values():
        try:
            f.result()
        except KafkaException as e:
            if e.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
                raise
    # Creation returns before every partition has a leader; until then reads fail with NOT_LEADER.
    deadline = time.monotonic() + 30
    while True:
        topics = admin.list_topics(timeout=10).topics
        if all(t in topics and topics[t].partitions and all(p.leader >= 0 for p in topics[t].partitions.values())
               for t in missing):
            return
        if time.monotonic() > deadline:
            raise TimeoutError(f"Kafka topics {missing} have no partition leaders after 30 s")
        time.sleep(0.2)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Create the RideSync Kafka topics")
    ap.add_argument("--bootstrap", default="localhost:9092")
    ap.add_argument("--partitions", type=int, default=3)
    ap.add_argument("--recreate", action="store_true", help="delete and recreate (wipes all runs)")
    args = ap.parse_args(argv)
    ensure_topics(args.bootstrap, args.partitions, args.recreate)
    print(f"topics ready: {', '.join(ALL_TOPICS)}")


if __name__ == "__main__":
    main()
