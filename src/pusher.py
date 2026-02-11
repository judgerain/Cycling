"""Convert planned workouts to API events and push to Intervals.icu calendar."""

from __future__ import annotations

from analyzer import check_fatigue, week_dates
from display import (
    bad, bold, header, ok, print_clean_preview, print_push_preview, warn,
)
from intervals_client import IntervalsClient
from models import PlannedWorkout

EXTERNAL_ID_PREFIX = "block-w"


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
    current_ids = {w.external_id for w in workouts if w.external_id}

    if dry_run:
        print_push_preview(events)
        print(f"\n  {bold('Dry run')} — {len(events)} events would be sent.")
        stale = clean_week(client, week, current_ids, dry_run=True)
        if not stale:
            print("  No stale events to clean.")
        print("  Run without --dry-run to push to Intervals.icu.")
        return

    print(f"Pushing {len(events)} events to Intervals.icu...")
    result = client.bulk_upsert_events(events)
    print(ok(f"  Done. {len(result)} events created/updated."))

    for e in result:
        status = "updated" if e.get("updated") else "created"
        print(f"    {e.get('start_date_local', '')[:10]} — {e.get('name', '')} [{status}]")

    # Auto-clean stale events
    stale = clean_week(client, week, current_ids)
    if stale:
        print(ok(f"  Cleaned {len(stale)} stale event(s)."))


def clean_week(
    client: IntervalsClient,
    week: int,
    current_ids: set[str],
    dry_run: bool = False,
) -> list[dict]:
    """Delete remote events for this week that aren't in current_ids."""
    monday, sunday = week_dates(week)
    remote = client.get_events(monday.isoformat(), sunday.isoformat())

    prefix = f"{EXTERNAL_ID_PREFIX}{week}-"
    stale = [
        e for e in remote
        if e.get("external_id", "").startswith(prefix)
        and e["external_id"] not in current_ids
    ]

    if not stale:
        return []

    if dry_run:
        print_clean_preview(stale)
        return stale

    for e in stale:
        client.delete_event(str(e["id"]))
        print(f"    Deleted: {e.get('start_date_local', '')[:10]} — {e.get('name', '')} [{e['external_id']}]")

    return stale


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
