"""Settings shared with docker compose: the environment first, then ``.env`` in the working directory.

The stack's passwords live in ``.env`` (copy ``.env.example``), which docker compose reads on its own.
Host-side services read the same file here, so nobody has to export anything.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import quote


def read_env_file(path: Path = Path(".env")) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip("'\"")
    return out


def setting(name: str, default: Optional[str] = None, path: Path = Path(".env")) -> Optional[str]:
    return os.environ.get(name) or read_env_file(path).get(name) or default


def pg_dsn() -> str:
    """The trip ledger's DSN: RIDESYNC_PG_DSN, else the compose Postgres with RIDESYNC_DB_PASSWORD."""
    dsn = setting("RIDESYNC_PG_DSN")
    if dsn:
        return dsn
    password = setting("RIDESYNC_DB_PASSWORD", "ridesync")
    return f"postgresql://ridesync:{quote(password, safe='')}@localhost:5432/ridesync"
