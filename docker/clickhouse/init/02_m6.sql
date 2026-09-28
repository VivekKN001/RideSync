-- M6: surge pricing. Runs after 01_schema.sql on a fresh data volume. For an existing volume
-- (init scripts only run once), apply it by hand; every statement is safe to repeat:
--   docker compose exec -T clickhouse clickhouse-client --multiquery < docker/clickhouse/init/02_m6.sql

-- Zone features gain app opens and price refusals (from `quoted` rider events).
ALTER TABLE ridesync.zone_features ADD COLUMN IF NOT EXISTS quotes UInt32 DEFAULT 0;
ALTER TABLE ridesync.zone_features ADD COLUMN IF NOT EXISTS declines UInt32 DEFAULT 0;

DROP VIEW IF EXISTS ridesync.mv_zone_features;
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
    JSONExtractUInt(raw, 'late') AS late,
    JSONExtractUInt(raw, 'quotes') AS quotes,
    JSONExtractUInt(raw, 'declines') AS declines
FROM ridesync.kafka_zone_features;

-- Surge prices: one row per zone per price update.
CREATE TABLE IF NOT EXISTS ridesync.zone_prices (
    run        LowCardinality(String),
    t          Float64,
    ts         DateTime64(3),
    zone       UInt16,
    multiplier Float64,
    demand     Float64,
    supply     Float64,
    source     LowCardinality(String)
) ENGINE = MergeTree ORDER BY (run, t, zone);

CREATE TABLE IF NOT EXISTS ridesync.kafka_zone_prices (raw String) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'kafka:19092', kafka_topic_list = 'zone-prices',
    kafka_group_name = 'clickhouse-zone-prices', kafka_format = 'JSONAsString';

CREATE MATERIALIZED VIEW IF NOT EXISTS ridesync.mv_zone_prices TO ridesync.zone_prices AS
SELECT
    JSONExtractString(raw, 'run') AS run,
    JSONExtractFloat(raw, 't') AS t,
    fromUnixTimestamp64Milli(JSONExtractInt(raw, 'ts')) AS ts,
    toUInt16OrZero(kv.1) AS zone,
    kv.2 AS multiplier,
    JSONExtractFloat(JSONExtractRaw(raw, 'demand'), kv.1) AS demand,
    JSONExtractFloat(JSONExtractRaw(raw, 'supply'), kv.1) AS supply,
    JSONExtractString(raw, 'source') AS source
FROM ridesync.kafka_zone_prices
ARRAY JOIN JSONExtractKeysAndValues(raw, 'prices', 'Float64') AS kv;
