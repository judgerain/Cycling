"""Pull data from Intervals.icu API and cache to data/*.json."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from intervals_client import IntervalsClient

DATA_DIR = Path(__file__).parent.parent / "data"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(exist_ok=True)


def save_json(filename: str, data: dict | list) -> Path:
    ensure_data_dir()
    path = DATA_DIR / filename
    path.write_text(json.dumps(data, indent=2, default=str))
    return path


def load_json(filename: str) -> dict | list | None:
    path = DATA_DIR / filename
    if path.exists():
        return json.loads(path.read_text())
    return None


def fetch_activities(client: IntervalsClient, days: int = 28) -> list[dict]:
    newest = date.today().isoformat()
    oldest = (date.today() - timedelta(days=days)).isoformat()
    data = client.get_activities(oldest, newest)
    save_json("activities.json", data)
    print(f"  Activities: {len(data)} fetched ({oldest} to {newest})")
    return data


def fetch_wellness(client: IntervalsClient, days: int = 28) -> list[dict]:
    newest = date.today().isoformat()
    oldest = (date.today() - timedelta(days=days)).isoformat()
    data = client.get_wellness(oldest, newest)
    save_json("wellness.json", data)
    print(f"  Wellness: {len(data)} days fetched")
    return data


def fetch_power_curves(client: IntervalsClient) -> dict | list:
    data = client.get_power_curves(sport="Ride", curves="42d")
    save_json("power_curves.json", data)
    print(f"  Power curves: fetched (42-day)")
    return data


def fetch_sport_settings(client: IntervalsClient) -> dict:
    data = client.get_sport_settings("Ride")
    save_json("sport_settings.json", data)
    print(f"  Sport settings: fetched")
    return data


def fetch_profile(client: IntervalsClient) -> dict:
    data = client.get_profile()
    save_json("profile.json", data)
    print(f"  Profile: fetched (athlete {data.get('id', '?')})")
    return data


def fetch_all(client: IntervalsClient, days: int = 28) -> dict:
    """Fetch all data sources and cache them."""
    print(f"Fetching data from Intervals.icu ({days} days)...")
    results = {}
    results["profile"] = fetch_profile(client)
    results["activities"] = fetch_activities(client, days)
    results["wellness"] = fetch_wellness(client, days)
    results["power_curves"] = fetch_power_curves(client)
    results["sport_settings"] = fetch_sport_settings(client)
    print("Done.")
    return results
