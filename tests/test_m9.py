"""M9: the public demo. In-memory demo run, the replay recording, the page modes, and the security settings
that make it safe to put the stack behind a tunnel."""
import gzip
import json
import re
import threading
import time
from pathlib import Path

import pytest

from ridesync.env import pg_dsn, read_env_file, setting
from ridesync.live.schema import DRIVER_EVENTS, RIDER_EVENTS
from ridesync.sim import SimConfig, simulate, summarize
from ridesync.stream.zones import ZONES_JSON
from ridesync.web.app import LiveView, render_page
from ridesync.web.demo import FeedBus, Stopped, run_once
from ridesync.web.record import Recorder, decode, record, write_site
from ridesync.web.share import grafana_problems

ROOT = Path(__file__).resolve().parents[1]
SMALL = SimConfig().with_(**{
    "demand.duration_s": 1200.0, "demand.warmup_s": 0.0, "demand.requests_per_hour": 900.0,
    "drivers.num_drivers": 60, "dispatch.strategy": "lsa", "dispatch.interval_s": 30.0,
})


# ---------------------------------------------------------------- settings
def test_env_file_parsing_and_precedence(tmp_path, monkeypatch):
    f = tmp_path / ".env"
    f.write_text("# comment\nA=1\n B = 'two' \nC=\"x=y\"\nnot a line\n", encoding="utf-8")
    assert read_env_file(f) == {"A": "1", "B": "two", "C": "x=y"}
    assert read_env_file(tmp_path / "missing") == {}
    monkeypatch.setenv("A", "from-env")
    assert setting("A", path=f) == "from-env"
    assert setting("B", path=f) == "two"
    assert setting("NOPE", "dflt", path=f) == "dflt"


def test_pg_dsn_quotes_the_password(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("RIDESYNC_PG_DSN", raising=False)
    monkeypatch.setenv("RIDESYNC_DB_PASSWORD", "p@ss/w:rd")
    assert pg_dsn() == "postgresql://ridesync:p%40ss%2Fw%3Ard@localhost:5432/ridesync"
    monkeypatch.setenv("RIDESYNC_PG_DSN", "postgresql://other")
    assert pg_dsn() == "postgresql://other"


# ------------------------------------------------------ what goes public
def _compose() -> str:
    return (ROOT / "docker-compose.yml").read_text(encoding="utf-8")


def test_every_port_is_loopback_only():
    ports = re.findall(r'^\s+- "([^"]+:\d+:\d+)"', _compose(), flags=re.M)
    assert ports, "no port mappings found"
    for p in ports:
        assert p.startswith(("127.0.0.1:", "[::1]:")), f"{p} listens beyond this machine"


def test_grafana_visitors_are_viewers_and_no_default_passwords():
    c = _compose()
    assert "GF_AUTH_ANONYMOUS_ORG_ROLE: Viewer" in c
    assert "GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD:?" in c
    assert not re.search(r"PASSWORD: ridesync\b", c)
    ds = (ROOT / "docker/grafana/provisioning/datasources/ridesync.yml").read_text(encoding="utf-8")
    assert "ridesync\n" not in ds.replace("database: ridesync\n", "").replace("defaultDatabase: ridesync\n", "")
    assert ds.count("$GRAFANA_DB_PASSWORD") == 2
    users = (ROOT / "docker/clickhouse/users.d/grafana.xml").read_text(encoding="utf-8")
    assert "<readonly>2</readonly>" in users and "GRANT SELECT ON ridesync.*" in users
    roles = (ROOT / "docker/postgres/init/02_roles.sh").read_text(encoding="utf-8")
    assert "default_transaction_read_only = on" in roles and "idle_in_transaction_session_timeout" in roles
    assert "GRANT SELECT ON ALL TABLES" in roles and "GRANT INSERT" not in roles


def test_share_refuses_the_example_admin_password(monkeypatch):
    example = read_env_file(ROOT / ".env.example")["GRAFANA_ADMIN_PASSWORD"]
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv("GRAFANA_ADMIN_PASSWORD", example)
    problems = grafana_problems("http://127.0.0.1:9")  # nothing listens on port 9
    assert any("example value" in p for p in problems)
    assert any("isn't answering" in p for p in problems)


def test_env_example_has_every_compose_variable():
    needed = set(re.findall(r"\$\{(\w+):\?", _compose()))
    assert needed <= set(read_env_file(ROOT / ".env.example"))


# ------------------------------------------------------------- demo run
def test_feed_bus_sends_pings_to_the_map_only():
    seen = []
    bus = FeedBus(seen.append)
    bus.produce(DRIVER_EVENTS, "1", {"type": "ping", "driver": 1, "pos": [40.7, -73.9]})
    bus.produce(RIDER_EVENTS, "2", {"type": "requested", "rider": 2})
    bus.produce("dispatch-offers", "3", {"type": "offer"})
    assert [m["type"] for m in seen] == ["ping", "requested"]
    assert [row[4] for row in bus.log] == ["requested", "offer"]


def test_demo_run_matches_the_offline_simulator():
    view = LiveView()
    sim = run_once(SMALL, view, 0.0, threading.Event())
    s = view.snapshot()
    assert s["ended"] and s["run"] == sim.run_id
    assert s["counts"]["requests"] == len(sim.riders)
    live, offline = summarize(sim), summarize(simulate(SMALL))
    # 1 s ticks instead of batch-interval ticks: same dispatch boundaries, near-identical outcome
    assert live["completed"] == pytest.approx(offline["completed"], rel=0.05)
    assert len(s["drivers"]) == SMALL.drivers.num_drivers


def test_demo_run_paces_and_stops():
    stop = threading.Event()
    threading.Timer(0.5, stop.set).start()
    t0 = time.monotonic()
    with pytest.raises(Stopped):
        run_once(SMALL, LiveView(), 100.0, stop)  # 1200 s at 100x would take 12 s
    assert time.monotonic() - t0 < 3.0


# ---------------------------------------------------------------- replay
def test_recording_round_trips_to_the_live_snapshots():
    view, rec, snaps = LiveView(), Recorder(), []

    def on_tick(t):
        if t % 60 == 0:
            s = view.snapshot()
            snaps.append(s)
            rec.add(s)

    run_once(SMALL, view, 0.0, threading.Event(), on_tick=on_tick)
    frames = decode(rec.document(60.0))
    assert len(frames) == len(snaps) > 10
    for s, f in zip(snaps, frames):
        assert f["t"] == round(s["t"]) and f["counts"] == s["counts"]
        for a, b in zip(sorted(s["drivers"]), f["drivers"]):
            assert a[0] == b[0] and a[3] == b[3]
            assert abs(a[1] - b[1]) < 1e-5 and abs(a[2] - b[2]) < 1e-5
            assert (a[3] == 1 and a[4] is not None) == (b[4] is not None)
        assert [w[0] for w in s["waiting"]] == [w[0] for w in f["waiting"]]
    # every match shows up exactly once across frames
    shown = [m[0] for f in frames for m in f["matches"]]
    assert len(shown) == len(set(shown))


def test_record_writes_a_static_site(tmp_path):
    doc = record(SMALL, step_s=30.0)
    assert doc["frames"][0]["t"] <= 1 and doc["frames"][-1]["t"] <= SMALL.demand.duration_s  # first tick: t = 1 s
    assert "60 drivers" in doc["note"]
    if not Path(ZONES_JSON).exists():
        pytest.skip(f"no {ZONES_JSON} (python -m ridesync.stream.zones) for the site's zone outlines")
    (tmp_path / "keep.txt").write_text("mine")
    write_site(doc, tmp_path)
    assert (tmp_path / "keep.txt").read_text() == "mine"  # only its own files are touched
    back = json.loads(gzip.decompress((tmp_path / "replay.json.gz").read_bytes()))
    assert back["frames"] == doc["frames"]
    page = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert 'const REPLAY = "replay.json.gz"' in page and "recorded run" in page


def test_page_modes_leave_no_placeholders():
    live = render_page("live", {"Grafana": "http://localhost:3000", "Flink UI": ""})
    assert not re.search(r"__[A-Z]+__", live)
    assert 'const REPLAY = ""' in live
    assert 'href="http://localhost:3000"' in live and "Flink UI" not in live
