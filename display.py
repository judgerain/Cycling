"""Terminal formatting with tabulate and ANSI colors."""

from __future__ import annotations

from tabulate import tabulate

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"


def colored(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def bold(text: str) -> str:
    return f"{BOLD}{text}{RESET}"


def header(text: str) -> str:
    return f"\n{BOLD}{CYAN}{'─' * 50}{RESET}\n{BOLD}{text}{RESET}\n{BOLD}{CYAN}{'─' * 50}{RESET}"


def section(text: str) -> str:
    return f"\n{BOLD}{text}{RESET}"


def ok(text: str) -> str:
    return colored(text, GREEN)


def warn(text: str) -> str:
    return colored(text, YELLOW)


def bad(text: str) -> str:
    return colored(text, RED)


def info(text: str) -> str:
    return colored(text, BLUE)


def table(rows: list[list], headers: list[str], fmt: str = "simple") -> str:
    return tabulate(rows, headers=headers, tablefmt=fmt)


def kv_table(pairs: list[tuple[str, str]]) -> str:
    return tabulate(pairs, tablefmt="plain")


# ── Formatters for specific data ────────────────────────

def format_hours(hours: float) -> str:
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h}h{m:02d}m"


def format_tsb(tsb: float | None) -> str:
    if tsb is None:
        return "—"
    if tsb < -20:
        return bad(f"{tsb:+.0f}")
    elif tsb < -10:
        return warn(f"{tsb:+.0f}")
    elif tsb > 10:
        return info(f"{tsb:+.0f}")
    return ok(f"{tsb:+.0f}")


def format_compliance(status: str) -> str:
    if status == "OK":
        return ok(status)
    elif status == "LOW":
        return warn(status)
    elif status == "HIGH":
        return bad(status)
    return status


def format_trend(current: float | None, previous: float | None) -> str:
    if current is None or previous is None:
        return "—"
    diff = current - previous
    if abs(diff) < 0.5:
        return f"{current:.0f} →"
    arrow = "↑" if diff > 0 else "↓"
    color = GREEN if diff > 0 else RED
    return colored(f"{current:.0f} {arrow}{abs(diff):.0f}", color)


def print_status_dashboard(
    ctl: float | None,
    atl: float | None,
    tsb: float | None,
    eftp: float | None,
    config_ftp: int,
    ramp_rate: float | None = None,
) -> None:
    print(header("Fitness Dashboard"))
    rows = [
        ["CTL (Fitness)", f"{ctl:.1f}" if ctl else "—"],
        ["ATL (Fatigue)", f"{atl:.1f}" if atl else "—"],
        ["TSB (Form)", format_tsb(tsb)],
        ["eFTP (detected)", f"{eftp:.0f}W" if eftp else "—"],
        ["Config FTP", f"{config_ftp}W"],
    ]
    if eftp and config_ftp:
        drift = eftp - config_ftp
        drift_str = f"{drift:+.0f}W"
        if abs(drift) > 5:
            drift_str = warn(drift_str + " (consider updating zones)")
        rows.append(["FTP Drift", drift_str])
    if ramp_rate is not None:
        rows.append(["Ramp Rate", f"{ramp_rate:.1f} TSS/wk"])
    print(kv_table(rows))


def print_week_summary(summary) -> None:
    from models import WeekSummary

    s: WeekSummary = summary
    print(header(f"Week {s.week_number} Summary — {s.phase}"))
    print(f"  {s.start_date} → {s.end_date}")
    print()

    rows = [
        ["Total Hours", format_hours(s.total_hours)],
        ["Planned Range", f"{s.planned_hours_min:.0f}–{s.planned_hours_max:.0f}h"],
        ["Compliance", format_compliance(s.compliance)],
        ["Total TSS", f"{s.total_tss:.0f}"],
        ["Rides", str(s.ride_count)],
        ["Strength", str(s.strength_count)],
    ]
    if s.ctl_end is not None:
        rows.append(["CTL (end)", f"{s.ctl_end:.1f}"])
    if s.tsb_end is not None:
        rows.append(["TSB (end)", format_tsb(s.tsb_end)])
    if s.eftp is not None:
        rows.append(["eFTP", f"{s.eftp:.0f}W"])
    print(kv_table(rows))

    if s.activities:
        print(section("\nActivities:"))
        act_rows = []
        for a in s.activities:
            watts = f"{a.average_watts:.0f}W" if a.average_watts else "—"
            hr = f"{a.average_heartrate:.0f}" if a.average_heartrate else "—"
            act_rows.append([
                str(a.date),
                a.name[:30],
                a.type,
                format_hours(a.hours),
                f"{a.icu_training_load:.0f}",
                watts,
                hr,
            ])
        print(table(
            act_rows,
            ["Date", "Name", "Type", "Time", "TSS", "Avg W", "Avg HR"],
        ))


def print_planned_workouts(workouts: list, week: int) -> None:
    print(header(f"Week {week} — Planned Workouts"))
    rows = []
    for w in workouts:
        has_structure = "Yes" if w.workout_text else "No"
        rows.append([
            str(w.date),
            _day_name(w.day_of_week),
            w.name[:35],
            w.workout_type,
            f"{w.duration_minutes}min" if w.duration_minutes else "—",
            w.zones,
            has_structure,
        ])
    print(table(
        rows,
        ["Date", "Day", "Name", "Type", "Duration", "Zones", "Structured"],
    ))


def print_push_preview(events: list[dict]) -> None:
    print(header("Push Preview — Events to Send"))
    rows = []
    for e in events:
        rows.append([
            e.get("start_date_local", "")[:10],
            e.get("name", ""),
            e.get("type", ""),
            e.get("external_id", ""),
        ])
    print(table(rows, ["Date", "Name", "Type", "External ID"]))


def _day_name(dow: int) -> str:
    return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dow]
