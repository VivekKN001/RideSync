"""NYC taxi zones: which zone a point is in.

    python -m ridesync.stream.zones        # taxi_zones.zip -> data/processed/taxi_zones.json

The index is dependency-free (a coarse grid over zone bounding boxes, then
ray casting), so it runs unchanged inside the Flink container. Zones are the
TLC's own areas: the historical demand is only available per zone, so the
M6 forecast can learn from it.
"""
from __future__ import annotations

import argparse
import json
import math
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ZONES_JSON = "data/processed/taxi_zones.json"
OUTSIDE = 0  # zone id for points in no zone (water, bridges, outside NYC)
Ring = List[Tuple[float, float]]  # (lat, lon)


def _in_ring(lat: float, lon: float, ring: Ring) -> bool:
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        yi, xi = ring[i]
        yj, xj = ring[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


class ZoneIndex:
    CELL_DEG = 0.01  # ~1 km grid cells

    def __init__(self, zones: Sequence[dict]):
        """``zones``: [{"id", "name", "borough", "polygons": [[[lat, lon], ...], ...]}]; only exterior rings."""
        self.names: Dict[int, str] = {z["id"]: z["name"] for z in zones}
        self.boroughs: Dict[int, str] = {z["id"]: z["borough"] for z in zones}
        self._polys: List[Tuple[int, Tuple[float, float, float, float], Ring]] = []
        self._grid: Dict[Tuple[int, int], List[int]] = {}
        for z in zones:
            for ring in z["polygons"]:
                ring = [(float(a), float(b)) for a, b in ring]
                lats, lons = [p[0] for p in ring], [p[1] for p in ring]
                box = (min(lats), max(lats), min(lons), max(lons))
                k = len(self._polys)
                self._polys.append((z["id"], box, ring))
                for gi in range(self._cell(box[0]), self._cell(box[1]) + 1):
                    for gj in range(self._cell(box[2]), self._cell(box[3]) + 1):
                        self._grid.setdefault((gi, gj), []).append(k)

    def _cell(self, v: float) -> int:
        return math.floor(v / self.CELL_DEG)

    def zone_of(self, lat: float, lon: float) -> int:
        for k in self._grid.get((self._cell(lat), self._cell(lon)), ()):
            zid, (a, b, c, d), ring = self._polys[k]
            if a <= lat <= b and c <= lon <= d and _in_ring(lat, lon, ring):
                return zid
        return OUTSIDE

    @classmethod
    def load(cls, path: str = ZONES_JSON) -> "ZoneIndex":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))


def build(zip_path: str = "data/raw/taxi_zones.zip", out: str = ZONES_JSON, tolerance_deg: float = 0.0001) -> List[dict]:
    """Taxi zone shapefile -> lat/lon JSON, simplified by ~10 m."""
    import geopandas as gpd

    with zipfile.ZipFile(zip_path) as z:
        shp = next(n for n in z.namelist() if n.endswith(".shp"))
    gdf = gpd.read_file(f"zip://{zip_path}!{shp}").to_crs(4326)
    zones = []
    for _, row in gdf.iterrows():
        geom = row.geometry.simplify(tolerance_deg)
        polys = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
        zones.append({
            "id": int(row["LocationID"]), "name": row["zone"], "borough": row["borough"],
            "polygons": [[[round(lat, 6), round(lon, 6)] for lon, lat in p.exterior.coords] for p in polys],
        })
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(zones, separators=(",", ":")), encoding="utf-8")
    return zones


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Build the taxi zone JSON used by the stream job and the live map")
    ap.add_argument("--zip", default="data/raw/taxi_zones.zip")
    ap.add_argument("--out", default=ZONES_JSON)
    args = ap.parse_args(argv)
    zones = build(args.zip, args.out)
    print(f"wrote {args.out}: {len(zones)} zones, {Path(args.out).stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    main()
