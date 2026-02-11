"""Parse plan/block_*.md files into PlannedWorkout objects."""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

from models import PlannedWorkout

PLAN_DIR = Path(__file__).parent / "plan"

# Maps day names from the markdown tables to weekday indices
DAY_MAP = {
    "mon": 0, "monday": 0,
    "tue": 1, "tuesday": 1,
    "wed": 2, "wednesday": 2,
    "thu": 3, "thursday": 3,
    "fri": 4, "friday": 4,
    "sat": 5, "saturday": 5,
    "sun": 6, "sunday": 6,
}


def find_block_file(week: int) -> Path | None:
    """Find the block markdown file that contains a given week."""
    for path in sorted(PLAN_DIR.glob("block_*.md")):
        text = path.read_text()
        # Look for "Week N" references in headers
        week_refs = re.findall(r"Week\s+(\d+)", text)
        weeks_in_block = [int(w) for w in week_refs]
        if week in weeks_in_block:
            return path
    return None


def parse_block(path: Path) -> list[PlannedWorkout]:
    """Parse an entire block file into PlannedWorkout objects."""
    text = path.read_text()
    workouts = []

    # Split into week sections by ## Week N headers
    week_sections = re.split(r"(?=^## Week \d+)", text, flags=re.MULTILINE)

    for section in week_sections:
        # Match headers like "## Week 1 (Feb 11–17)" or "## Week 3 (Feb 25 – Mar 3)"
        match = re.match(
            r"## Week (\d+)\s+\(([A-Za-z]+ \d+)\s*[–-]\s*([A-Za-z ]*\d+(?:,?\s*\d{4})?)\)",
            section,
        )
        if not match:
            continue

        week_num = int(match.group(1))
        week_start = _parse_week_start(match.group(2), match.group(3))
        if not week_start:
            continue

        # Extract workouts from the table
        table_workouts = _parse_week_table(section, week_num, week_start)

        # Extract structured workout code blocks keyed by day-of-week
        structured = _parse_workout_blocks(section)

        # Match structured workouts to table entries by day-of-week
        # Skip WeightTraining — structured workout text is always cycling
        for w in table_workouts:
            if (w.day_of_week in structured
                    and not w.workout_text
                    and w.workout_type != "WeightTraining"):
                w.workout_text = structured[w.day_of_week]
            workouts.append(w)

    return workouts


def parse_week(week: int) -> list[PlannedWorkout]:
    """Parse workouts for a specific week."""
    path = find_block_file(week)
    if not path:
        return []
    all_workouts = parse_block(path)
    return [w for w in all_workouts if w.week == week]


def _parse_week_start(start_str: str, end_str: str) -> date | None:
    """Parse 'Feb 11' or 'Mar 3' into a date, inferring year from context."""
    months = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    # Try to parse start_str like "Feb 11"
    parts = start_str.strip().split()
    if len(parts) < 2:
        return None
    month_str = parts[0].lower()[:3]
    day = int(parts[1].rstrip(","))
    month = months.get(month_str)
    if not month:
        return None

    # Check end_str for year, default to 2026 (plan year)
    year = 2026
    year_match = re.search(r"(\d{4})", end_str)
    if year_match:
        year = int(year_match.group(1))

    return date(year, month, day)


def _parse_week_table(section: str, week_num: int, week_start: date) -> list[PlannedWorkout]:
    """Extract workouts from the markdown table in a week section."""
    workouts = []

    # Find table rows (lines starting with |)
    table_lines = [
        line for line in section.split("\n")
        if line.strip().startswith("|") and not line.strip().startswith("|---")
    ]

    # Skip header row
    if table_lines and "Day" in table_lines[0]:
        table_lines = table_lines[1:]

    for line in table_lines:
        cells = [c.strip().strip("*").strip() for c in line.split("|")]
        cells = [c for c in cells if c]  # remove empty from leading/trailing |

        if len(cells) < 4:
            continue

        day_str = cells[0].lower().strip("*").strip()
        session_name = cells[1]
        duration_str = cells[2] if len(cells) > 2 else ""
        description = cells[3] if len(cells) > 3 else ""
        zones = cells[4] if len(cells) > 4 else ""

        # Map day to weekday index
        dow = None
        for key, val in DAY_MAP.items():
            if key in day_str:
                dow = val
                break
        if dow is None:
            continue

        # Skip REST days
        if "rest" in session_name.lower() and "rest" == session_name.strip().lower():
            continue
        if session_name.strip() == "**REST**":
            continue

        # Parse duration
        duration_min = _parse_duration(duration_str)

        # Determine workout type
        workout_type = _infer_type(session_name, description)

        workout_date = week_start + timedelta(days=dow)
        external_id = f"block-w{week_num}-{_day_abbr(dow)}-{_slugify(session_name)}"

        workouts.append(PlannedWorkout(
            week=week_num,
            day_of_week=dow,
            date=workout_date,
            name=session_name,
            description=description,
            duration_minutes=duration_min,
            workout_type=workout_type,
            zones=zones,
            external_id=external_id,
        ))

    return workouts


def _parse_workout_blocks(section: str) -> dict[int, str]:
    """Extract workout code blocks keyed by day-of-week.

    Looks for patterns like:
        ### Tuesday — Sweet Spot Intro
        ```
        - 10min 55%
        ...
        ```
    Returns {day_of_week: workout_text}.
    """
    blocks = {}
    pattern = re.compile(
        r"###\s+(\w+)\s*[—–-]\s*.+?\n"   # heading with day name
        r".*?"                              # optional text between
        r"```\n(.*?)```",                   # code block
        re.DOTALL,
    )
    for match in pattern.finditer(section):
        day_name = match.group(1).lower()
        workout_text = match.group(2).strip()
        for key, dow in DAY_MAP.items():
            if key == day_name or day_name == key:
                blocks[dow] = workout_text
                break

    return blocks


def _parse_duration(s: str) -> int:
    """Parse duration strings like '60min', '1h45', '1h15 + 35min', '45-60min'."""
    if not s:
        return 0
    # Handle ranges: take the higher value
    if "+" in s:
        parts = s.split("+")
        return sum(_parse_duration(p.strip()) for p in parts)
    if "–" in s or "-" in s:
        parts = re.split(r"[–-]", s)
        return max(_parse_single_duration(p.strip()) for p in parts if p.strip())
    return _parse_single_duration(s)


def _parse_single_duration(s: str) -> int:
    """Parse a single duration value."""
    s = s.strip().lower()
    if not s or s == "—":
        return 0
    # Match "1h45" or "1h" or "45min" or "45m" or "30min"
    match = re.match(r"(\d+)h(\d+)?m?", s)
    if match:
        hours = int(match.group(1))
        mins = int(match.group(2) or 0)
        return hours * 60 + mins
    match = re.match(r"(\d+)\s*min", s)
    if match:
        return int(match.group(1))
    # Plain number — assume minutes
    match = re.match(r"(\d+)", s)
    if match:
        return int(match.group(1))
    return 0


def _infer_type(name: str, description: str) -> str:
    """Infer Intervals.icu activity type from session name/description.

    Name takes priority over description to avoid false matches
    (e.g. "Easy spin" with description "after strength" isn't WeightTraining).
    """
    name_lower = name.lower()
    # Check name first — it's the authoritative source
    if "strength" in name_lower or "weight" in name_lower:
        return "WeightTraining"
    if "indoor" in name_lower or "rouvy" in name_lower:
        return "VirtualRide"
    if "outdoor" in name_lower or "long" in name_lower:
        return "Ride"
    # Check for spin/easy as indoor rides
    if "spin" in name_lower:
        return "VirtualRide"
    return "Ride"


def _day_abbr(dow: int) -> str:
    return ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][dow]


def _slugify(s: str) -> str:
    """Simple slugify for external IDs."""
    s = re.sub(r"[^a-z0-9]+", "-", s.lower())
    return s.strip("-")[:30]
