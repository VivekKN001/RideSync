"""Share the live map from this laptop over free Cloudflare quick tunnels.

    python -m ridesync.web.share --demo        # no Docker: the in-memory demo, public link in ~10 s
    python -m ridesync.web.share               # the full stack (start it first, see the README), + read-only Grafana

Quick tunnels need no Cloudflare account, and every start gets new random https://….trycloudflare.com
links. Only the map and Grafana go out; everything else in the stack listens on 127.0.0.1. Before
exposing Grafana this checks that visitors can't edit and that the admin password isn't the example
one. The map's Grafana link then points at the public Grafana. Ctrl+C closes the tunnels.

cloudflared: on PATH, in tools/, or --cloudflared. Install with `winget install Cloudflare.cloudflared`
(or download it from github.com/cloudflare/cloudflared/releases).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path
from typing import List, Optional

from ..env import read_env_file, setting
from .app import app_from_args, build_parser

URL = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")
GRAFANA_LOCAL = "http://localhost:3000"


def find_cloudflared(explicit: Optional[str] = None) -> str:
    if explicit:
        return explicit
    for c in (shutil.which("cloudflared"), "tools/cloudflared.exe", "tools/cloudflared"):
        if c and Path(c).is_file():
            return str(Path(c).resolve())  # Windows won't start a relative path
    sys.exit("cloudflared not found: `winget install Cloudflare.cloudflared`, or put it in tools/ (see this module's doc)")


class Tunnel:
    """One quick tunnel: cloudflared forwarding a public trycloudflare.com URL to a local port."""

    def __init__(self, exe: str, local_url: str, timeout_s: float = 45.0):
        self.proc = subprocess.Popen([exe, "tunnel", "--no-autoupdate", "--url", local_url],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors="replace")
        self.url: Optional[str] = None
        found = threading.Event()

        def read() -> None:  # keeps draining stderr afterwards, so cloudflared never blocks on a full pipe
            for line in self.proc.stderr:
                m = URL.search(line)
                if m and self.url is None:
                    self.url = m.group(0)
                    found.set()
            found.set()

        threading.Thread(target=read, daemon=True).start()
        if not found.wait(timeout_s) or self.url is None:
            self.close()
            raise RuntimeError(f"cloudflared gave no public URL for {local_url} within {timeout_s:.0f} s")

    def close(self) -> None:
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(5)
            except subprocess.TimeoutExpired:
                self.proc.kill()


def grafana_problems(base: str = GRAFANA_LOCAL) -> List[str]:
    """Reasons not to put this Grafana on the internet (empty = fine)."""
    problems = []
    admin_pw = setting("GRAFANA_ADMIN_PASSWORD")
    example = read_env_file(Path(".env.example")).get("GRAFANA_ADMIN_PASSWORD")
    if not admin_pw or admin_pw == example:
        problems.append("GRAFANA_ADMIN_PASSWORD in .env is missing or still the example value")
    try:
        urllib.request.urlopen(f"{base}/api/health", timeout=3).read()
    except (urllib.error.URLError, OSError):
        return problems + [f"Grafana isn't answering on {base} (docker compose --profile storage up -d)"]
    req = urllib.request.Request(f"{base}/api/dashboards/db", method="POST", headers={"Content-Type": "application/json"},
                                 data=json.dumps({"dashboard": {"title": "share check"}}).encode())
    try:
        urllib.request.urlopen(req, timeout=5)
        problems.append("anonymous visitors can create dashboards (GF_AUTH_ANONYMOUS_ORG_ROLE must be Viewer)")
    except urllib.error.HTTPError as e:
        if e.code not in (401, 403):
            problems.append(f"unexpected answer to an anonymous edit: HTTP {e.code}")
    return problems


def main(argv=None) -> None:
    import uvicorn

    sys.stdout.reconfigure(encoding="utf-8")
    ap = build_parser(__doc__.split("\n")[0])
    ap.add_argument("--cloudflared", default=None, help="path to cloudflared")
    ap.add_argument("--no-grafana", action="store_true", help="share the map only")
    args = ap.parse_args(argv)
    exe = find_cloudflared(args.cloudflared)

    tunnels: List[Tunnel] = []
    try:
        grafana = ""
        if not args.demo and not args.no_grafana:
            problems = grafana_problems()
            if problems:
                sys.exit("not sharing Grafana:\n  - " + "\n  - ".join(problems) + "\n(fix these, or use --no-grafana)")
            print("opening a tunnel for Grafana …", flush=True)
            tunnels.append(Tunnel(exe, GRAFANA_LOCAL))
            grafana = tunnels[-1].url
        print("opening a tunnel for the map …", flush=True)
        tunnels.append(Tunnel(exe, f"http://localhost:{args.port}"))
        app = app_from_args(args, grafana=grafana, flink="")  # Flink's UI can submit jobs: it stays local
        print(f"\n  live map   {tunnels[-1].url}" + (f"\n  grafana    {grafana}  (read-only)" if grafana else ""))
        print("\nThe links work while this runs (a few seconds after start, while DNS catches up). Ctrl+C stops.\n",
              flush=True)
        uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
    finally:
        for t in tunnels:
            t.close()


if __name__ == "__main__":
    main()
