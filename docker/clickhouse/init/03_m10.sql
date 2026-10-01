-- M10: the matcher's repositioning moves and the simulator's answers. Runs after 02_m6.sql on a fresh data
-- volume. For an existing volume (init scripts only run once), apply it by hand; every statement is safe to repeat:
--   docker compose exec -T clickhouse clickhouse-client --multiquery < docker/clickhouse/init/03_m10.sql

CREATE TABLE IF NOT EXISTS ridesync.reposition_moves (
    run     LowCardinality(String),
    type    LowCardinality(String),   -- move (sent by the matcher) or move_response (from the simulator)
    move_id String,
    driver  UInt32,
    zone    UInt16,
    outcome LowCardinality(String),   -- move_response: started or rejected
    reason  LowCardinality(String),   -- rejected: driver_busy, expired or no_route
    t       Float64,
    ts      DateTime64(3)
) ENGINE = MergeTree ORDER BY (run, t, driver);

CREATE TABLE IF NOT EXISTS ridesync.kafka_reposition_moves (raw String) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'kafka:19092', kafka_topic_list = 'reposition-moves',
    kafka_group_name = 'clickhouse-reposition-moves', kafka_format = 'JSONAsString';

CREATE MATERIALIZED VIEW IF NOT EXISTS ridesync.mv_reposition_moves TO ridesync.reposition_moves AS
SELECT
    JSONExtractString(raw, 'run') AS run,
    JSONExtractString(raw, 'type') AS type,
    JSONExtractString(raw, 'move_id') AS move_id,
    JSONExtractUInt(raw, 'driver') AS driver,
    JSONExtractUInt(raw, 'zone') AS zone,
    JSONExtractString(raw, 'outcome') AS outcome,
    JSONExtractString(raw, 'reason') AS reason,
    JSONExtractFloat(raw, 't') AS t,
    -- the matcher's moves carry no ts (event time as epoch ms); its wall clock at sending stands in
    if(JSONHas(raw, 'ts'), fromUnixTimestamp64Milli(JSONExtractInt(raw, 'ts')),
       toDateTime64(JSONExtractFloat(raw, 'wall'), 3)) AS ts
FROM ridesync.kafka_reposition_moves;
