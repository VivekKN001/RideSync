-- RideSync trip ledger: one row per trip, updated through its life by ridesync.sinks.postgres.
-- Runs once, on the first start with an empty data volume.

CREATE TABLE runs (
    run_id     text PRIMARY KEY,
    started_at timestamptz,
    ended_at   timestamptz,
    config     jsonb
);

-- Order of a trip's states; an update never moves a trip backwards (events can arrive out of order).
CREATE FUNCTION trip_rank(status text) RETURNS int LANGUAGE sql IMMUTABLE AS $$
    SELECT CASE status WHEN 'requested' THEN 0 WHEN 'matched' THEN 1 WHEN 'picked_up' THEN 2
                       WHEN 'dropped_off' THEN 3 WHEN 'cancelled' THEN 3 ELSE -1 END
$$;

CREATE TABLE trips (
    run_id         text        NOT NULL,
    rider_id       integer     NOT NULL,
    status         text        NOT NULL,
    requested_s    double precision,  -- simulated seconds since the run started
    matched_s      double precision,
    picked_up_s    double precision,
    finished_s     double precision,  -- dropped off or cancelled
    requested_at   timestamptz,       -- event time (wall clock the event was due)
    origin_lat     double precision,
    origin_lon     double precision,
    dest_lat       double precision,
    dest_lon       double precision,
    driver_id      integer,
    quoted_eta_s   double precision,
    cancel_reason  text,
    updated_at     timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (run_id, rider_id)
);
CREATE INDEX trips_run_status ON trips (run_id, status);
CREATE INDEX trips_updated ON trips (updated_at DESC);
