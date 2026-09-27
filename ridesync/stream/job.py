"""PyFlink job: per-zone, per-minute features from the world topics.

Submitted inside the Flink cluster (see docker-compose.yml):

    docker compose run --rm flink-submit                          # defaults below
    docker compose run --rm flink-submit --lateness-ms 5000

    rider-events ─┐                                        ┌─► zone-features
                  ├─► watermarks ─► by rider/driver ─► by (run, zone) ─┤
    driver-events ┘   (event time   Enrich: zone +      ZoneFeatures:  └─► late-events
                       = "ts")      supply changes      minute windows

Watermarks are per Kafka partition with bounded out-of-orderness
(``--lateness-ms``), idle partitions excluded after 5 s. The simulator's ticks
keep them moving when nothing else happens. State lives in Flink keyed state
and is checkpointed every 10 s, so a restarted job resumes where it stopped.
All the logic is in ``ridesync.stream.features``; this file only wires it up.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from pyflink.common import Duration, Types, WatermarkStrategy
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.time import Time
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.datastream import CheckpointingMode, OutputTag, StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    DeliveryGuarantee, KafkaOffsetsInitializer, KafkaRecordSerializationSchema, KafkaSink, KafkaSource,
)
from pyflink.datastream.functions import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import StateTtlConfig, ValueStateDescriptor

from ridesync.live.schema import DRIVER_EVENTS, LATE_EVENTS, RIDER_EVENTS, ZONE_FEATURES
from ridesync.stream.features import (
    add_event, close_until, enrich, entity_key, new_zone_state, zone_key,
)
from ridesync.stream.zones import ZoneIndex

LATE = OutputTag("late-events", Types.STRING())
_TS = re.compile(r'"ts":(\d+)')


class EventTime(TimestampAssigner):
    def extract_timestamp(self, value, record_timestamp) -> int:
        m = _TS.search(value)
        return int(m.group(1)) if m else record_timestamp


class Enrich(KeyedProcessFunction):
    """Keyed by rider or driver: attach zones, turn statuses into supply changes."""

    def __init__(self, zones_path: str):
        self.zones_path = zones_path

    def open(self, ctx: RuntimeContext):
        self.zones = ZoneIndex.load(self.zones_path)
        desc = ValueStateDescriptor("entity", Types.PICKLED_BYTE_ARRAY())
        desc.enable_time_to_live(StateTtlConfig.new_builder(Time.hours(6)).build())  # abandoned runs
        self.state = ctx.get_state(desc)

    def process_element(self, value, ctx):
        st, events = enrich(self.state.value(), value, self.zones)
        if st is None:
            self.state.clear()
        else:
            self.state.update(st)
        yield from events


class ZoneFeatures(KeyedProcessFunction):
    """Keyed by (run, zone): count per simulated minute, emit a row when the watermark passes its end."""

    def open(self, ctx: RuntimeContext):
        desc = ValueStateDescriptor("zone", Types.PICKLED_BYTE_ARRAY())
        desc.enable_time_to_live(StateTtlConfig.new_builder(Time.hours(6)).build())
        self.state = ctx.get_state(desc)

    def process_element(self, ev, ctx):
        st = self.state.value() or new_zone_state()
        if add_event(st, ev):
            yield LATE, json.dumps({**ev, "type": "late"}, separators=(",", ":"))
        self.state.update(st)
        for end in st["ends"].values():
            ctx.timer_service().register_event_time_timer(end)

    def on_timer(self, timestamp, ctx):
        st = self.state.value()
        if st is None:
            return
        run, zone = ctx.get_current_key().rsplit("|", 1)
        for row in close_until(st, run, int(zone), timestamp):
            yield json.dumps(row, separators=(",", ":"))
        self.state.update(st)
        for end in st["ends"].values():
            ctx.timer_service().register_event_time_timer(end)


def kafka_sink(bootstrap: str, topic: str) -> KafkaSink:
    return (KafkaSink.builder()
            .set_bootstrap_servers(bootstrap)
            .set_record_serializer(KafkaRecordSerializationSchema.builder()
                                   .set_topic(topic)
                                   .set_value_serialization_schema(SimpleStringSchema())
                                   .build())
            .set_delivery_guarantee(DeliveryGuarantee.AT_LEAST_ONCE)
            .build())


def build(env: StreamExecutionEnvironment, args) -> None:
    p = args.prefix
    offsets = KafkaOffsetsInitializer.earliest() if args.start == "earliest" else KafkaOffsetsInitializer.latest()
    source = (KafkaSource.builder()
              .set_bootstrap_servers(args.bootstrap)
              .set_topics(p + RIDER_EVENTS, p + DRIVER_EVENTS)
              .set_group_id(f"{p}flink-zone-features")
              .set_starting_offsets(offsets)
              .set_value_only_deserializer(SimpleStringSchema())
              .build())
    watermarks = (WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_millis(args.lateness_ms))
                  .with_timestamp_assigner(EventTime())
                  .with_idleness(Duration.of_seconds(5)))

    events = (env.from_source(source, watermarks, "world events")
              .map(json.loads, output_type=Types.PICKLED_BYTE_ARRAY()).name("parse")
              .filter(lambda m: entity_key(m) is not None).name("riders and driver statuses"))
    zone_events = (events.key_by(entity_key, key_type=Types.STRING())
                   .process(Enrich(args.zones), output_type=Types.PICKLED_BYTE_ARRAY()).name("enrich: zones"))
    rows = (zone_events.key_by(zone_key, key_type=Types.STRING())
            .process(ZoneFeatures(), output_type=Types.STRING()).name("zone minute windows"))
    rows.sink_to(kafka_sink(args.bootstrap, p + ZONE_FEATURES)).name("zone-features")
    rows.get_side_output(LATE).sink_to(kafka_sink(args.bootstrap, p + LATE_EVENTS)).name("late-events")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="RideSync zone features (PyFlink)")
    ap.add_argument("--bootstrap", default="kafka:19092")
    ap.add_argument("--prefix", default="", help="topic name prefix")
    ap.add_argument("--zones", default="/opt/data/taxi_zones.json")
    ap.add_argument("--lateness-ms", type=int, default=2000, help="bounded out-of-orderness of the watermark")
    ap.add_argument("--start", choices=["latest", "earliest"], default="latest")
    ap.add_argument("--parallelism", type=int, default=2)
    args = ap.parse_args(argv)

    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(args.parallelism)
    env.enable_checkpointing(10_000, CheckpointingMode.AT_LEAST_ONCE)
    build(env, args)
    env.execute(f"ridesync zone features (lateness {args.lateness_ms} ms)")


if __name__ == "__main__":
    main(sys.argv[1:])
