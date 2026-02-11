"""Weekly summary, compliance, fatigue, and zone analysis."""

from __future__ import annotations

import tomllib
from datetime import date, timedelta
from pathlib import Path

from models import Activity, WellnessDay, WeekSummary, FitnessSnapshot
from fetcher import load_json

CONFIG_PATH = Path(__file__).parent / "config.toml"


def load_config() -> dict:
    return tomllib.loads(CONFIG_PATH.read_text())


def get_plan_start() -> date:
    cfg = load_config()
    return date.fromisoformat(cfg["plan"]["start_date"])


def week_dates(week_number: int) -> tuple[date, date]:
    """Return (Monday, Sunday) for a given training week number."""
    start = get_plan_start()
    week_start = start + timedelta(weeks=week_number - 1)
    # Align to Monday
    week_start -= timedelta(days=week_start.weekday())
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def get_phase(week_number: int) -> tuple[str, float, float]:
    """Return (phase_name, min_hours, max_hours) for a week number."""
    cfg = load_config()
    for name, bounds in cfg["phases"].items():
        start_w, end_w, min_h, max_h = bounds
        if start_w <= week_number <= end_w:
            label = name.replace("_", " ").title()
            return label, float(min_h), float(max_h)
    return "Unknown", 0, 0


def current_week_number() -> int:
    """Calculate which training week we're in based on plan start date."""
    start = get_plan_start()
    today = date.today()
    delta = (today - start).days
    return max(1, delta // 7 + 1)


def load_activities() -> list[Activity]:
    data = load_json("activities.json")
    if not data:
        return []
    return [Activity.from_api(a) for a in data]


def load_wellness() -> list[WellnessDay]:
    data = load_json("wellness.json")
    if not data:
        return []
    return [WellnessDay.from_api(w) for w in data]


def get_latest_fitness() -> FitnessSnapshot | None:
    wellness = load_wellness()
    if not wellness:
        return None
    # Find the most recent day with CTL data
    for w in reversed(wellness):
        if w.ctl is not None:
            return FitnessSnapshot(
                date=w.date,
                ctl=w.ctl,
                atl=w.atl or 0,
                eftp=w.eftp,
            )
    return None


def analyze_week(week_number: int) -> WeekSummary:
    """Build a WeekSummary from cached data."""
    start, end = week_dates(week_number)
    phase, min_h, max_h = get_phase(week_number)

    activities = load_activities()
    wellness = load_wellness()

    # Filter activities for this week
    week_activities = [
        a for a in activities
        if start <= a.date <= end
    ]

    # Totals
    total_hours = sum(a.hours for a in week_activities)
    total_tss = sum(a.icu_training_load for a in week_activities)
    ride_count = sum(
        1 for a in week_activities
        if a.type in ("Ride", "VirtualRide", "MountainBikeRide")
    )
    strength_count = sum(
        1 for a in week_activities
        if a.type == "WeightTraining"
    )

    # Wellness for this week
    week_wellness = [w for w in wellness if start <= w.date <= end]

    ctl_start = None
    ctl_end = None
    atl_end = None
    tsb_end = None
    eftp = None
    avg_soreness = None
    avg_fatigue = None

    if week_wellness:
        first = week_wellness[0]
        last = week_wellness[-1]
        ctl_start = first.ctl
        ctl_end = last.ctl
        atl_end = last.atl
        tsb_end = last.tsb
        # Find most recent eFTP in the week
        for w in reversed(week_wellness):
            if w.eftp:
                eftp = w.eftp
                break
        # Average subjective scores
        soreness_vals = [w.soreness for w in week_wellness if w.soreness]
        fatigue_vals = [w.fatigue for w in week_wellness if w.fatigue]
        if soreness_vals:
            avg_soreness = sum(soreness_vals) / len(soreness_vals)
        if fatigue_vals:
            avg_fatigue = sum(fatigue_vals) / len(fatigue_vals)

    return WeekSummary(
        week_number=week_number,
        start_date=start,
        end_date=end,
        phase=phase,
        total_hours=total_hours,
        total_tss=total_tss,
        ride_count=ride_count,
        strength_count=strength_count,
        planned_hours_min=min_h,
        planned_hours_max=max_h,
        ctl_start=ctl_start,
        ctl_end=ctl_end,
        atl_end=atl_end,
        tsb_end=tsb_end,
        eftp=eftp,
        avg_soreness=avg_soreness,
        avg_fatigue=avg_fatigue,
        activities=week_activities,
    )


def check_fatigue(week_number: int) -> dict:
    """Check if athlete is overly fatigued, suggest adjustments."""
    cfg = load_config()
    tsb_warning = cfg["fatigue"]["tsb_warning"]
    power_reduction = cfg["fatigue"]["power_reduction"]

    summary = analyze_week(week_number)
    result = {
        "fatigued": False,
        "tsb": summary.tsb_end,
        "message": "",
        "power_reduction": 0.0,
    }

    if summary.tsb_end is not None and summary.tsb_end < tsb_warning:
        result["fatigued"] = True
        result["power_reduction"] = power_reduction
        result["message"] = (
            f"TSB is {summary.tsb_end:+.0f} (below {tsb_warning}). "
            f"Reducing power targets by {power_reduction * 100:.0f}%."
        )
    return result


def check_zones(config_ftp: int) -> dict:
    """Compare configured FTP vs detected eFTP."""
    cfg = load_config()
    drift_threshold = cfg["fatigue"]["eftp_drift_threshold"]

    fitness = get_latest_fitness()
    if not fitness or not fitness.eftp:
        return {"drift": 0, "eftp": None, "message": "No eFTP data available."}

    drift = fitness.eftp - config_ftp
    message = f"Config FTP: {config_ftp}W | eFTP: {fitness.eftp:.0f}W | Drift: {drift:+.0f}W"
    if abs(drift) > drift_threshold:
        message += f"\n  → Consider updating FTP to {fitness.eftp:.0f}W and recalculating zones."

    return {"drift": drift, "eftp": fitness.eftp, "message": message}
