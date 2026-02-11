#!/usr/bin/env python

"""CLI entry point for the Intervals.icu training integration."""

from __future__ import annotations

import argparse
import sys

from analyzer import (
    analyze_week,
    check_zones,
    current_week_number,
    get_latest_fitness,
    load_config,
)
from display import (
    bad,
    bold,
    header,
    ok,
    print_planned_workouts,
    print_status_dashboard,
    print_week_summary,
    section,
    warn,
)
from fetcher import fetch_all
from intervals_client import IntervalsClient
from planner import parse_week
from pusher import clean_week, push_week


def cmd_fetch(args: argparse.Namespace) -> None:
    client = IntervalsClient()
    fetch_all(client, days=args.days)


def cmd_analyze(args: argparse.Namespace) -> None:
    week = args.week or current_week_number()
    summary = analyze_week(week)
    print_week_summary(summary)


def cmd_plan_week(args: argparse.Namespace) -> None:
    week = args.week or current_week_number() + 1
    workouts = parse_week(week)
    if not workouts:
        print(bad(f"No workouts found for week {week}."))
        print("  Check that a plan/block_*.md file covers this week.")
        sys.exit(1)

    print_planned_workouts(workouts, week)

    # Show structured workout details
    for w in workouts:
        if w.workout_text:
            print(section(f"\n{w.date} — {w.name}"))
            print(w.workout_text)

    if args.dry_run:
        print(f"\n  {bold('Dry run')} — workouts parsed but not pushed.")


def cmd_push(args: argparse.Namespace) -> None:
    week = args.week or current_week_number() + 1
    workouts = parse_week(week)
    if not workouts:
        print(bad(f"No workouts found for week {week}."))
        sys.exit(1)

    client = IntervalsClient()
    push_week(client, workouts, week, dry_run=args.dry_run)


def cmd_clean(args: argparse.Namespace) -> None:
    week = args.week or current_week_number() + 1
    workouts = parse_week(week)
    current_ids = {w.external_id for w in workouts if w.external_id}

    client = IntervalsClient()
    stale = clean_week(client, week, current_ids, dry_run=args.dry_run)

    if not stale:
        print(ok(f"No stale events for week {week}."))
    elif args.dry_run:
        print(f"\n  {bold('Dry run')} — {len(stale)} event(s) would be deleted.")
        print("  Run without --dry-run to delete.")
    else:
        print(ok(f"  Deleted {len(stale)} stale event(s) for week {week}."))


def cmd_status(args: argparse.Namespace) -> None:
    cfg = load_config()
    config_ftp = cfg["athlete"]["ftp"]
    fitness = get_latest_fitness()

    if not fitness:
        print(warn("No fitness data cached. Run 'python main.py fetch' first."))
        return

    print_status_dashboard(
        ctl=fitness.ctl,
        atl=fitness.atl,
        tsb=fitness.tsb,
        eftp=fitness.eftp,
        config_ftp=config_ftp,
        ramp_rate=fitness.ramp_rate,
    )

    print(f"\n  Data from: {fitness.date}")
    print(f"  Current training week: {current_week_number()}")


def cmd_zones(args: argparse.Namespace) -> None:
    cfg = load_config()
    config_ftp = cfg["athlete"]["ftp"]

    print(header("Zone Check"))

    result = check_zones(config_ftp)
    print(f"\n  {result['message']}")

    if result["eftp"] and abs(result["drift"]) > cfg["fatigue"]["eftp_drift_threshold"]:
        new_ftp = int(result["eftp"])
        zones = cfg["zones"]
        print(section(f"\nSuggested zones at FTP {new_ftp}W:"))
        for zone_name, pct in zones.items():
            watts = int(new_ftp * pct / 100)
            print(f"  {zone_name.upper()}: {pct}% → {watts}W")

        answer = input(f"\n  Update FTP to {new_ftp}W in config.toml? [y/N] ").strip().lower()
        if answer in ("y", "yes"):
            _update_config_ftp(new_ftp)
            print(ok(f"  Updated config.toml: ftp = {new_ftp}"))
        else:
            print("  No changes made.")


def _update_config_ftp(new_ftp: int) -> None:
    """Update the ftp value in config.toml (preserves file structure)."""
    import re
    from pathlib import Path

    config_path = Path(__file__).parent.parent / "config.toml"
    text = config_path.read_text()
    text = re.sub(r"^(ftp\s*=\s*)\d+", rf"\g<1>{new_ftp}", text, count=1, flags=re.MULTILINE)
    config_path.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Intervals.icu training integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Workflow: fetch → analyze → plan-week --dry-run → push | clean",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # fetch
    fetch_days_default = 7 * 4 * 6
    p_fetch = sub.add_parser("fetch", help="Pull data from Intervals.icu")
    p_fetch.add_argument("--days", type=int, default=fetch_days_default,
                         help=f"Days of history (default: {fetch_days_default})")

    # analyze
    p_analyze = sub.add_parser("analyze", help="Show weekly training summary")
    p_analyze.add_argument("--week", type=int, help="Week number (default: current)")

    # plan-week
    p_plan = sub.add_parser("plan-week", help="Parse block markdown into workouts")
    p_plan.add_argument("--week", type=int, help="Week number (default: next week)")
    p_plan.add_argument("--dry-run", action="store_true", help="Preview only")

    # push
    p_push = sub.add_parser("push", help="Push workouts to Intervals.icu calendar")
    p_push.add_argument("--week", type=int, help="Week number (default: next week)")
    p_push.add_argument("--dry-run", action="store_true", help="Preview API payloads without sending")

    # clean
    p_clean = sub.add_parser("clean", help="Remove stale events from Intervals.icu calendar")
    p_clean.add_argument("--week", type=int, help="Week number (default: next week)")
    p_clean.add_argument("--dry-run", action="store_true", help="Preview stale events without deleting")

    # status
    sub.add_parser("status", help="Quick fitness dashboard")

    # zones
    sub.add_parser("zones", help="Compare configured FTP vs detected eFTP")

    args = parser.parse_args()

    commands = {
        "fetch": cmd_fetch,
        "analyze": cmd_analyze,
        "plan-week": cmd_plan_week,
        "push": cmd_push,
        "clean": cmd_clean,
        "status": cmd_status,
        "zones": cmd_zones,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
