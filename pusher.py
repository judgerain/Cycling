"""Convert planned workouts to API events and push to Intervals.icu calendar."""

from __future__ import annotations

from analyzer import check_fatigue
from display import (
    bad, bold, header, ok, print_push_preview, warn,
)
from intervals_client import IntervalsClient
from models import PlannedWorkout


def prepare_events(
    workouts: list[PlannedWorkout],
    fatigue_adjust: bool = True,
    week: int | None = None,
) -> list[dict]:
    """Convert PlannedWorkout list to API event payloads.

    If fatigue_adjust is True, checks TSB and reduces power targets when fatigued.
    """
    events = []
    reduction = 0.0

    if fatigue_adjust and week:
        fatigue = check_fatigue(week - 1)  # check previous week
        if fatigue["fatigued"]:
            reduction = fatigue["power_reduction"]
            print(warn(f"  ⚠ {fatigue['message']}"))

    for w in workouts:
        event = w.to_event()
        if event.get("description"):
            event["description"] = _normalize_durations(event["description"])
        if reduction > 0 and w.workout_text:
            event["description"] = _reduce_power(event["description"], reduction)
            event["name"] = f"{w.name} (adjusted -{reduction * 100:.0f}%)"
        events.append(event)

    return events


def push_week(
    client: IntervalsClient,
    workouts: list[PlannedWorkout],
    week: int,
    dry_run: bool = False,
) -> None:
    """Push a week of workouts to Intervals.icu calendar."""
    if not workouts:
        print("No workouts to push.")
        return

    events = prepare_events(workouts, fatigue_adjust=True, week=week)

    if dry_run:
        print_push_preview(events)
        print(f"\n  {bold('Dry run')} — {len(events)} events would be sent.")
        print("  Run without --dry-run to push to Intervals.icu.")
        return

    print(f"Pushing {len(events)} events to Intervals.icu...")
    result = client.bulk_upsert_events(events)
    print(ok(f"  Done. {len(result)} events created/updated."))

    for e in result:
        status = "updated" if e.get("updated") else "created"
        print(f"    {e.get('start_date_local', '')[:10]} — {e.get('name', '')} [{status}]")


def _normalize_durations(text: str) -> str:
    """Normalize duration format: 'min' → 'm' for Intervals.icu compatibility.

    '10min 55%' → '10m 55%' (Intervals.icu needs 'm' not 'min' to generate steps).
    """
    import re
    return re.sub(r"(\d+)min\b", r"\1m", text)


def _reduce_power(workout_text: str, reduction: float) -> str:
    """Reduce percentage targets in workout text.

    E.g., with reduction=0.05: '88%' becomes '84%', '100%' becomes '95%'.
    """
    import re

    def adjust(match: re.Match) -> str:
        pct = int(match.group(1))
        new_pct = int(pct * (1 - reduction))
        return f"{new_pct}%"

    # Match standalone percentages (not part of other patterns)
    return re.sub(r"(\d+)%", adjust, workout_text)
