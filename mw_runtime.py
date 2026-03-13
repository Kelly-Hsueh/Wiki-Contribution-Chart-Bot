from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
from requests import Response

DEFAULT_USER_AGENT: str = (
    "WikiChartBot/1.0 (https://github.com/your-org/your-repo; "
    "contact@example.org) requests/2.x")


def load_env_file(env_path: str = ".env") -> None:
    path = Path(env_path)
    if not path.exists() or not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if ((value.startswith('"') and value.endswith('"'))
                or (value.startswith("'") and value.endswith("'"))):
            value = value[1:-1]

        os.environ.setdefault(key, value)


def safe_get_json(response: Response) -> dict[str, Any]:
    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"API returned non-JSON response, HTTP {response.status_code}"
        ) from exc


def build_session(user_agent: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": user_agent,
        "Accept-Encoding": "gzip",
    })
    return session
