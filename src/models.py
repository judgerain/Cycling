"""Dataclasses for the Intervals.icu training integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Activity:
    id: str
    date: date
    name: str
    type: str  # Ride, VirtualRide, WeightTraining, etc.
    moving_time: int  # seconds
    distance: float  # meters
    icu_training_load: float  # TSS equivalent
    icu_intensity: float  # IF equivalent
    average_watts: float | None = None
    normalized_power: float | None = None
    average_heartrate: float | None = None
    total_elevation_gain: float | None = None

    @classmethod
    def from_api(cls, data: dict) -> Activity:
        return cls(
            id=str(data["id"]),
            date=date.fromisoformat(data["start_date_local"][:10]),
            name=data.get("name", ""),
            type=data.get("type", "Ride"),
            moving_time=data.get("moving_time", 0),
            distance=data.get("distance", 0.0),
            icu_training_load=data.get("icu_training_load") or 0.0,
            icu_intensity=data.get("icu_intensity") or 0.0,
            average_watts=data.get("icu_average_watts") or data.get("average_watts"),
            normalized_power=data.get("icu_weighted_avg_watts"),
            average_heartrate=data.get("average_heartrate"),
            total_elevation_gain=data.get("total_elevation_gain"),
        )

    @property
    def hours(self) -> float:
        return self.moving_time / 3600


@dataclass
class WellnessDay:
    date: date
    ctl: float | None = None  # chronic training load (fitness)
    atl: float | None = None  # acute training load (fatigue)
    resting_hr: int | None = None
    weight: float | None = None
    sleep_secs: int | None = None
    soreness: int | None = None  # 1-4 (1=good)
    fatigue: int | None = None  # 1-4 (1=good)
    mood: int | None = None  # 1-4 (1=good)
    eftp: float | None = None  # estimated FTP from Intervals.icu

    @classmethod
    def from_api(cls, data: dict) -> WellnessDay:
        return cls(
            date=date.fromisoformat(data["id"]),
            ctl=data.get("ctl"),
            atl=data.get("atl"),
            resting_hr=data.get("restingHR"),
            weight=data.get("weight"),
            sleep_secs=data.get("sleepSecs"),
            soreness=data.get("soreness"),
            fatigue=data.get("fatigue"),
            mood=data.get("mood"),
            eftp=data.get("Ride_eftp"),
        )

    @property
    def tsb(self) -> float | None:
        if self.ctl is not None and self.atl is not None:
            return self.ctl - self.atl
        return None


@dataclass
class FitnessSnapshot:
    date: date
    ctl: float
    atl: float
    eftp: float | None = None
    ramp_rate: float | None = None

    @property
    def tsb(self) -> float:
        return self.ctl - self.atl


@dataclass
class PlannedWorkout:
    week: int
    day_of_week: int  # 0=Monday
    date: date
    name: str
    description: str  # human-readable description
    workout_text: str | None = None  # Intervals.icu workout format
    duration_minutes: int = 0
    workout_type: str = "Ride"  # Ride, VirtualRide, WeightTraining
    zones: str = ""  # e.g. "Z2-Z4"
    external_id: str = ""  # for upsert matching

    def to_event(self) -> dict:
        """Convert to Intervals.icu event API payload."""
        event = {
            "category": "WORKOUT",
            "start_date_local": f"{self.date.isoformat()}T00:00:00",
            "type": self.workout_type,
            "name": self.name,
            "external_id": self.external_id,
        }
        if self.workout_text:
            event["description"] = self.workout_text
        else:
            event["description"] = self.description
        if self.duration_minutes:
            event["moving_time"] = self.duration_minutes * 60
        return event


@dataclass
class WeekSummary:
    week_number: int
    start_date: date
    end_date: date
    phase: str
    total_hours: float = 0.0
    total_tss: float = 0.0
    ride_count: int = 0
    strength_count: int = 0
    planned_hours_min: float = 0.0
    planned_hours_max: float = 0.0
    ctl_start: float | None = None
    ctl_end: float | None = None
    atl_end: float | None = None
    tsb_end: float | None = None
    eftp: float | None = None
    avg_soreness: float | None = None
    avg_fatigue: float | None = None
    activities: list[Activity] = field(default_factory=list)

    @property
    def compliance(self) -> str:
        if self.planned_hours_max == 0:
            return "N/A"
        if self.total_hours < self.planned_hours_min * 0.8:
            return "LOW"
        elif self.total_hours > self.planned_hours_max * 1.1:
            return "HIGH"
        return "OK"
