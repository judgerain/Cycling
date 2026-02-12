# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cycling training project of amateur cyclist with Intervals.icu integration for data-driven coaching.

## Environment

- **Python**: 3.14.3 (CPython)
- **Virtual environment**: `venv_p/` (activate with `source venv_p/bin/activate`)
- **IDE**: PyCharm
- **Dependencies**: `requests`, `python-dotenv`, `tabulate` (see `requirements.txt`)

## Project Structure

### Training Plans (source of truth)
- `training_plan.md` — Master plan: zones (FTP 263W), 25-week periodization, weekly structure, strength plan, progress tracking
- `plan/block_1_base_rebuild.md` — Weeks 1–4 detailed daily workouts
- `plan/intervals_format.md` — Intervals.icu workout text format reference
- Future blocks: `plan/block_N_*.md`

### Intervals.icu Integration (Python — `src/`)
- `src/main.py` — CLI entry point: `fetch`, `analyze`, `plan-week`, `push`, `status`, `zones`
- `src/intervals_client.py` — API wrapper (Basic auth, throttle)
- `src/fetcher.py` — Pull data → cache to `data/*.json`
- `src/analyzer.py` — Weekly summaries, compliance, fatigue, zone drift
- `src/planner.py` — Parse `plan/block_*.md` → PlannedWorkout objects
- `src/pusher.py` — Convert workouts → API events, bulk upsert
- `src/models.py` — Dataclasses (Activity, WellnessDay, FitnessSnapshot, PlannedWorkout, WeekSummary)
- `src/display.py` — Terminal formatting (tabulate, ANSI colors)

### Config
- `config.toml` — Athlete metrics (FTP, weight, zones), plan dates, phase targets
- `.env` — API key (git-ignored)
- `data/` — JSON cache (git-ignored)

## Coaching Context

- **Event**: Pyrenees 2500km / ~70,000m, early August 2026
- **Plan start**: Monday Feb 9, 2026 (calendar-aligned, Mon–Sun weeks)
- **Current FTP**: 263W (Intervals.icu setting), eFTP ~260W
- **Schedule**: 5 cycling days + 2 strength days, Friday full rest
- **Indoor platform**: Rouvy (workouts in Intervals.icu text format)
- **Long rides**: Weekends (Sat/Sun)
- **No formal FTP tests** — track eFTP from Intervals.icu, flag when zones drift >5W
- **Weekly feedback**: Athlete provides RPE, hours, fatigue ratings → coach adjusts next week
- **Fatigue guard**: If TSB < -20, reduce power targets by 5%

## Intervals.icu Workout Format

- Use `m` for minutes, `s` for seconds, `h` for hours (e.g. `10m 55%`, `30s 130%`)
- **Never use `min`** — it displays as text but does not generate structured workout steps
- Always keep strength (WeightTraining) and cycling (Ride/VirtualRide) as separate table rows — different types break the workout format
- See `plan/intervals_format.md` for full reference

## CLI Workflow

```
python src/main.py fetch              # Pull data from Intervals.icu
python src/main.py analyze --week 1   # Weekly summary
python src/main.py plan-week --week 1 --dry-run  # Preview parsed workouts
python src/main.py push --week 1      # Push to Intervals.icu calendar
python src/main.py status             # Fitness dashboard
python src/main.py zones              # FTP drift check
```

## Project details

I’d like you to become my new cycling coach and help me create a customized training plan. Below, I’ve added some details to guide you in designing a plan that fits my goals, timeline, and lifestyle:

- I’m an amateur cyclist, not a performance athlete, but I’m looking to improve.
- I want to analyze and plan trainings
- My time for training is limited, so I want a plan that prioritizes “bang for buck” workouts—maximizing results in the time I can commit.
- Format: Provide the plan as a diary with daily workouts, broken down into:
    - Indoor Workouts (Rouvy): Include a corresponding workout that matches the session (database here: [Zwift Workouts](https://whatsonzwift.com/workouts)) in format https://forum.intervals.icu/t/workout-builder/1163.
    - Outdoor Rides: Keep these simple and enjoyable—no need for constant stat-checking if no structure highly needed
- Limit tests if it is possible. And try track progress from trainings 
- Let me know how to provide weekly feedback so you can adapt the plan as we go.
- Present the training plan in a table format for easy reference.
- Include clear descriptions of each workout and its purpose (e.g., endurance, power, recovery)
- Give me an indication of the metrics (e.g power, hard rate or exertion level) that the workout should be done at.

**Goals:**

1. My primary cycling goal is ultra endurance rides by mountains and improve my FTP to ride long climbs it good pace
2. My secondary cycling goal is to improve my 5 - 20 min power efforts to fly on local short climbs fast.
3. In middle summer I'm planing to ride 2500 km multiday self supported endurance ride by the Pyrenees with assent ~70000 meters   

**Current Fitness Level:**

1. I restarted my training 3 month ago. Before I had FTP 280 watts.
2. I currently cycle ~4 times per week and a total time of 3-4 per week. This my second week after pause.
3. In addition to cycling, I also do some workout training but not regular

**Limitations:**

1. I can dedicate about 15 hours to training outdoors. Or 8-10 indoors. I located in Gijon so you can check weather
2. I don’t like long zone 2 rides on indoor training and in general prefer outdoor, because indoor rides are boring
3. The equipment I have available includes road bike with power meter and pulse meter, interactive trainer

**Metrics:**

1. I track my rides with heart rate monitor and power meter and my typical stats are 260 FTP now (max FTP I ever gotten 278), heart rate  LT1: 130-132, LT2 ~160 max HR ~ 175, weight 76 kg height 170

**Likes/Dislikes:**

1. I enjoy  hilly rides, long rides, ultra endurance rides the most about cycling.
2. I struggle with or dislike flat rides but in my location currently hard to find flat routes. As negative on my hilly and mountain terrain It's hard to stick to zone 2 
3. I’m also interested in adding more structured workout sessions.