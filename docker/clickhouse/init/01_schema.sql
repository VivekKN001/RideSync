-- RideSync event history. ClickHouse reads Kafka itself: each topic has a Kafka-engine table
-- (one raw JSON string per message) and a materialized view that parses it into a MergeTree table.
-- Runs once, on the first start with an empty data volume.

CREATE DATABASE IF NOT EXISTS ridesync;

-- ------------------------------------------------------------------ zones
CREATE TABLE ridesync.zones (id UInt16, borough String, name String, service_zone String)
ENGINE = MergeTree ORDER BY id;
INSERT INTO ridesync.zones
SELECT LocationID, Borough, Zone, service_zone  -- CSVWithNames matches columns by header name
FROM file('taxi_zone_lookup.csv', 'CSVWithNames', 'LocationID UInt16, Borough String, Zone String, service_zone String');

-- ------------------------------------------------------------ rider events
CREATE TABLE ridesync.rider_events (
    run          LowCardinality(String),
    type         LowCardinality(String),
    rider        UInt32,
    t            Float64,
    ts           DateTime64(3),
    driver       Int32,
    quoted_eta_s Nullable(Float64),
    reason       LowCardinality(String),
    origin_lat   Float64,
    origin_lon   Float64,
    request_t    Nullable(Float64)
) ENGINE = MergeTree ORDER BY (run, t, rider);

CREATE TABLE ridesync.kafka_rider_events (raw String) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'kafka:19092', kafka_topic_list = 'rider-events',
    kafka_group_name = 'clickhouse-rider-events', kafka_format = 'JSONAsString';

CREATE TABLE ridesync.run_markers (
    run        LowCardinality(String),
    kind       LowCardinality(String),
    t          Float64,
    ts         DateTime64(3),
    started_ms Int64,
    config     String
) ENGINE = ReplacingMergeTree ORDER BY (run, kind);

CREATE MATERIALIZED VIEW ridesync.mv_rider_events TO ridesync.rider_events AS
SELECT
    JSONExtractString(raw, 'run') AS run,
    JSONExtractString(raw, 'type') AS type,
    JSONExtractUInt(raw, 'rider') AS rider,
    JSONExtractFloat(raw, 't') AS t,
    fromUnixTimestamp64Milli(JSONExtractInt(raw, 'ts')) AS ts,
    if(JSONHas(raw, 'driver') AND JSONType(raw, 'driver') = 'Int64', JSONExtractInt(raw, 'driver'), -1) AS driver,
    if(JSONHas(raw, 'quoted_eta_s'), JSONExtractFloat(raw, 'quoted_eta_s'), NULL) AS quoted_eta_s,
    JSONExtractString(raw, 'reason') AS reason,
    JSONExtractFloat(raw, 'origin', 1) AS origin_lat,
    JSONExtractFloat(raw, 'origin', 2) AS origin_lon,
    if(JSONHas(raw, 'request_t'), JSONExtractFloat(raw, 'request_t'), NULL) AS request_t
FROM ridesync.kafka_rider_events
WHERE JSONExtractString(raw, 'type') NOT IN ('run_start', 'tick', 'run_end');

-- run_start / run_end are written to every partition; ReplacingMergeTree keeps one per (run, kind).
CREATE MATERIALIZED VIEW ridesync.mv_run_markers TO ridesync.run_markers AS
SELECT
    JSONExtractString(raw, 'run') AS run,
    JSONExtractString(raw, 'type') AS kind,
    JSONExtractFloat(raw, 't') AS t,
    fromUnixTimestamp64Milli(JSONExtractInt(raw, 'ts')) AS ts,
    JSONExtractInt(raw, 'started_ms') AS started_ms,
    JSONExtractRaw(raw, 'config') AS config
FROM ridesync.kafka_rider_events
WHERE JSONExtractString(raw, 'type') IN ('run_start', 'run_end');

-- ----------------------------------------------------------- driver events
CREATE TABLE ridesync.driver_status (
    run      LowCardinality(String),
    driver   UInt32,
    seq      UInt32,
    state    LowCardinality(String),
    lat      Float64,
    lon      Float64,
    free_at  Float64,
    has_next UInt8,
    t        Float64,
    ts       DateTime64(3)
) ENGINE = MergeTree ORDER BY (run, driver, t, seq);

CREATE TABLE ridesync.driver_pings (
    run    LowCardinality(String),
    driver UInt32,
    lat    Float64,
    lon    Float64,
    t      Float64,
    ts     DateTime64(3)
) ENGINE = MergeTree ORDER BY (run, t, driver) TTL toDateTime(ts) + INTERVAL 1 DAY;

CREATE TABLE ridesync.kafka_driver_events (raw String) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'kafka:19092', kafka_topic_list = 'driver-events',
    kafka_group_name = 'clickhouse-driver-events', kafka_format = 'JSONAsString',
    kafka_max_block_size = 16384;  -- pings are the biggest stream: small blocks keep memory flat

CREATE MATERIALIZED VIEW ridesync.mv_driver_status TO ridesync.driver_status AS
SELECT
    JSONExtractString(raw, 'run') AS run,
    JSONExtractUInt(raw, 'driver') AS driver,
    JSONExtractUInt(raw, 'seq') AS seq,
    JSONExtractString(raw, 'state') AS state,
    JSONExtractFloat(raw, 'pos', 1) AS lat,
    JSONExtractFloat(raw, 'pos', 2) AS lon,
    JSONExtractFloat(raw, 'free_at') AS free_at,
    JSONExtractBool(raw, 'has_next') AS has_next,
    JSONExtractFloat(raw, 't') AS t,
    fromUnixTimestamp64Milli(JSONExtractInt(raw, 'ts')) AS ts
FROM ridesync.kafka_driver_events
WHERE JSONExtractString(raw, 'type') = 'status';

CREATE MATERIALIZED VIEW ridesync.mv_driver_pings TO ridesync.driver_pings AS
SELECT
    JSONExtractString(raw, 'run') AS run,
    JSONExtractUInt(raw, 'driver') AS driver,
    JSONExtractFloat(raw, 'pos', 1) AS lat,
    JSONExtractFloat(raw, 'pos', 2) AS lon,
    JSONExtractFloat(raw, 't') AS t,
    fromUnixTimestamp64Milli(JSONExtractInt(raw, 'ts')) AS ts
FROM ridesync.kafka_driver_events
WHERE JSONExtractString(raw, 'type') = 'ping';

-- ---------------------------------------------------------- offer responses
CREATE TABLE ridesync.offer_responses (
    run      LowCardinality(String),
    offer_id String,
    rider    UInt32,
    driver   UInt32,
    outcome  LowCardinality(String),
    reason   LowCardinality(String),
    t        Float64,
    ts       DateTime64(3)
) ENGINE = MergeTree ORDER BY (run, t);

CREATE TABLE ridesync.kafka_offer_responses (raw String) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'kafka:19092', kafka_topic_list = 'offer-responses',
    kafka_group_name = 'clickhouse-offer-responses', kafka_format = 'JSONAsString';

CREATE MATERIALIZED VIEW ridesync.mv_offer_responses TO ridesync.offer_responses AS
SELECT
    JSONExtractString(raw, 'run') AS run,
    JSONExtractString(raw, 'offer_id') AS offer_id,
    JSONExtractUInt(raw, 'rider') AS rider,
    JSONExtractUInt(raw, 'driver') AS driver,
    JSONExtractString(raw, 'outcome') AS outcome,
    JSONExtractString(raw, 'reason') AS reason,
    JSONExtractFloat(raw, 't') AS t,
    fromUnixTimestamp64Milli(JSONExtractInt(raw, 'ts')) AS ts
FROM ridesync.kafka_offer_responses;

-- ---------------------------------------------------------- matcher batches
CREATE TABLE ridesync.dispatch_batches (
    run         LowCardinality(String),
    seq         UInt32,
    batch_t     Float64,
    riders      UInt32,
    drivers     UInt32,
    offers      UInt32,
    solve_ms    Float64,
    cost        Nullable(Float64),
    shadow_cost Nullable(Float64),
    skipped     UInt32,
    tick_lag_ms Nullable(Float64),
    ts          DateTime64(3)
) ENGINE = MergeTree ORDER BY (run, batch_t);

CREATE TABLE ridesync.kafka_dispatch_batches (raw String) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'kafka:19092', kafka_topic_list = 'dispatch-batches',
    kafka_group_name = 'clickhouse-dispatch-batches', kafka_format = 'JSONAsString';

CREATE MATERIALIZED VIEW ridesync.mv_dispatch_batches TO ridesync.dispatch_batches AS
SELECT
    JSONExtractString(raw, 'run') AS run,
    JSONExtractUInt(raw, 'seq') AS seq,
    JSONExtractFloat(raw, 'batch_t') AS batch_t,
    JSONExtractUInt(raw, 'riders') AS riders,
    JSONExtractUInt(raw, 'drivers') AS drivers,
    JSONExtractUInt(raw, 'offers') AS offers,
    JSONExtractFloat(raw, 'solve_ms') AS solve_ms,
    if(JSONType(raw, 'cost') = 'Double', JSONExtractFloat(raw, 'cost'), NULL) AS cost,
    if(JSONType(raw, 'shadow_cost') = 'Double', JSONExtractFloat(raw, 'shadow_cost'), NULL) AS shadow_cost,
    JSONExtractUInt(raw, 'skipped') AS skipped,
    if(JSONType(raw, 'tick_lag_ms') = 'Double', JSONExtractFloat(raw, 'tick_lag_ms'), NULL) AS tick_lag_ms,
    fromUnixTimestamp64Milli(JSONExtractInt(raw, 'ts')) AS ts
FROM ridesync.kafka_dispatch_batches;

-- ------------------------------------------------ Flink output: zone features
CREATE TABLE ridesync.zone_features (
    run              LowCardinality(String),
    zone             UInt16,
    minute           UInt32,
    t                Float64,
    ts               DateTime64(3),
    requests         UInt32,
    matches          UInt32,
    cancels_no_match UInt32,
    cancels_eta      UInt32,
    pickups          UInt32,
    dropoffs         UInt32,
    match_wait_sum   Float64,
    eta_sum          Float64,
    pickup_wait_sum  Float64,
    idle_end         Int32,
    late             UInt32
) ENGINE = ReplacingMergeTree ORDER BY (run, zone, minute);  -- at-least-once sink: duplicates collapse

CREATE TABLE ridesync.kafka_zone_features (raw String) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'kafka:19092', kafka_topic_list = 'zone-features',
    kafka_group_name = 'clickhouse-zone-features', kafka_format = 'JSONAsString';

CREATE MATERIALIZED VIEW ridesync.mv_zone_features TO ridesync.zone_features AS
SELECT
    JSONExtractString(raw, 'run') AS run,
    JSONExtractUInt(raw, 'zone') AS zone,
    JSONExtractUInt(raw, 'minute') AS minute,
    JSONExtractFloat(raw, 't') AS t,
    fromUnixTimestamp64Milli(JSONExtractInt(raw, 'ts')) AS ts,
    JSONExtractUInt(raw, 'requests') AS requests,
    JSONExtractUInt(raw, 'matches') AS matches,
    JSONExtractUInt(raw, 'cancels_no_match') AS cancels_no_match,
    JSONExtractUInt(raw, 'cancels_eta') AS cancels_eta,
    JSONExtractUInt(raw, 'pickups') AS pickups,
    JSONExtractUInt(raw, 'dropoffs') AS dropoffs,
    JSONExtractFloat(raw, 'match_wait_sum') AS match_wait_sum,
    JSONExtractFloat(raw, 'eta_sum') AS eta_sum,
    JSONExtractFloat(raw, 'pickup_wait_sum') AS pickup_wait_sum,
    JSONExtractInt(raw, 'idle_end') AS idle_end,
    JSONExtractUInt(raw, 'late') AS late
FROM ridesync.kafka_zone_features;

CREATE TABLE ridesync.late_events (
    run      LowCardinality(String),
    zone     UInt16,
    kind     LowCardinality(String),
    t        Float64,
    ts       DateTime64(3),
    received DateTime64(3) DEFAULT now64(3)
) ENGINE = MergeTree ORDER BY (run, t);

CREATE TABLE ridesync.kafka_late_events (raw String) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'kafka:19092', kafka_topic_list = 'late-events',
    kafka_group_name = 'clickhouse-late-events', kafka_format = 'JSONAsString';

CREATE MATERIALIZED VIEW ridesync.mv_late_events TO ridesync.late_events AS
SELECT
    JSONExtractString(raw, 'run') AS run,
    JSONExtractUInt(raw, 'zone') AS zone,
    JSONExtractString(raw, 'kind') AS kind,
    JSONExtractFloat(raw, 't') AS t,
    fromUnixTimestamp64Milli(JSONExtractInt(raw, 'ts')) AS ts,
    now64(3) AS received
FROM ridesync.kafka_late_events;
