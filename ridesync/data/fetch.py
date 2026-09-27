"""Download raw inputs into data/ (idempotent: existing files are skipped).

    python -m ridesync.data.fetch --tlc 2024-03 --osm
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Sequence

TLC_BASE = "https://d37ci6vzurychx.cloudfront.net"
# BBBike's New York extract covers NYC plus a margin (~150 MB), far smaller than the
# whole-state Geofabrik file, whose OSRM preprocessing needs ~6 GB RAM.
OSM_NYC = "https://download.bbbike.org/osm/bbbike/NewYork/NewYork.osm.pbf"

RAW = Path("data/raw")
OSM = Path("data/osm")


def download(url: str, dest: Path) -> None:
    import requests

    if dest.exists() and dest.stat().st_size > 0:
        print(f"exists: {dest}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    print(f"downloading {url}")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    tmp.replace(dest)
    print(f"wrote {dest} ({dest.stat().st_size / 1e6:.0f} MB)")


def main(argv: Optional[Sequence[str]] = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tlc", nargs="*", default=[], metavar="YYYY-MM", help="high-volume FHV months to fetch")
    ap.add_argument("--osm", action="store_true", help="NYC OpenStreetMap extract for OSRM")
    args = ap.parse_args(argv)

    download(f"{TLC_BASE}/misc/taxi_zones.zip", RAW / "taxi_zones.zip")
    download(f"{TLC_BASE}/misc/taxi_zone_lookup.csv", RAW / "taxi_zone_lookup.csv")
    for month in args.tlc:
        download(f"{TLC_BASE}/trip-data/fhvhv_tripdata_{month}.parquet", RAW / f"fhvhv_tripdata_{month}.parquet")
    if args.osm:
        download(OSM_NYC, OSM / "nyc.osm.pbf")


if __name__ == "__main__":
    main()
