"""Thin API wrapper for Intervals.icu."""

from __future__ import annotations

import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://intervals.icu/api/v1"
REQUEST_INTERVAL = 0.12  # ~8 req/s, well under the 30/s limit


class IntervalsClient:
    def __init__(
        self,
        api_key: str | None = None,
        athlete_id: str | None = None,
    ):
        self.api_key = api_key or os.getenv("INTERVALS_API_KEY", "")
        self.athlete_id = athlete_id or os.getenv("INTERVALS_ATHLETE_ID", "0")
        if not self.api_key:
            raise ValueError(
                "INTERVALS_API_KEY not set. "
                "Copy .env.example to .env and add your key."
            )
        self._session = requests.Session()
        self._session.auth = ("API_KEY", self.api_key)
        self._session.headers["Content-Type"] = "application/json"
        self._last_request = 0.0

    def _url(self, path: str) -> str:
        return f"{BASE_URL}/athlete/{self.athlete_id}/{path}"

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < REQUEST_INTERVAL:
            time.sleep(REQUEST_INTERVAL - elapsed)
        self._last_request = time.monotonic()

    def _get(self, path: str, params: dict | None = None) -> dict | list:
        self._throttle()
        resp = self._session.get(self._url(path), params=params)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, json_data: dict | list, params: dict | None = None) -> dict | list:
        self._throttle()
        resp = self._session.post(self._url(path), json=json_data, params=params)
        resp.raise_for_status()
        return resp.json()

    def _put(self, path: str, json_data: dict) -> dict:
        self._throttle()
        resp = self._session.put(self._url(path), json=json_data)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str) -> None:
        self._throttle()
        resp = self._session.delete(self._url(path))
        resp.raise_for_status()

    # ── Activities ──────────────────────────────────────────

    def get_activities(self, oldest: str, newest: str) -> list[dict]:
        return self._get("activities", {"oldest": oldest, "newest": newest})

    # ── Wellness (includes CTL/ATL/eFTP) ────────────────────

    def get_wellness(self, oldest: str, newest: str) -> list[dict]:
        return self._get("wellness", {"oldest": oldest, "newest": newest})

    # ── Athlete profile (sport settings, zones) ─────────────

    def get_profile(self) -> dict:
        self._throttle()
        resp = self._session.get(f"{BASE_URL}/athlete/{self.athlete_id}")
        resp.raise_for_status()
        return resp.json()

    def get_sport_settings(self, sport: str = "Ride") -> dict:
        return self._get(f"sport-settings/{sport}")

    # ── Power curves ────────────────────────────────────────

    def get_power_curves(self, sport: str = "Ride", curves: str = "42d") -> dict | list:
        return self._get("power-curves", {"type": sport, "curves": curves})

    # ── Events (calendar workouts) ──────────────────────────

    def get_events(self, oldest: str, newest: str) -> list[dict]:
        return self._get("events", {"oldest": oldest, "newest": newest})

    def create_event(self, event: dict) -> dict:
        return self._post("events", event)

    def update_event(self, event_id: str, event: dict) -> dict:
        return self._put(f"events/{event_id}", event)

    def delete_event(self, event_id: str) -> None:
        self._delete(f"events/{event_id}")

    def bulk_upsert_events(self, events: list[dict]) -> list[dict]:
        return self._post("events/bulk", events, params={"upsert": "true"})

    # ── Convenience ─────────────────────────────────────────

    def ping(self) -> bool:
        """Test connection by fetching athlete profile."""
        try:
            profile = self.get_profile()
            return "id" in profile
        except requests.RequestException:
            return False
