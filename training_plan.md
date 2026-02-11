# Cycling Training Plan — Pyrenees 2500km Preparation

**Athlete**: Amateur cyclist, 76.4kg, 170cm
**Current FTP**: 263W (3.44 W/kg)
**Target Event**: Pyrenees 2500km / ~70,000m ascent, early August 2026
**Plan Start**: Monday Feb 9, 2026 (~25 weeks out)
**Location**: Gijón, Spain (hilly terrain)

---

## Training Zones

### Power Zones (based on FTP 263W)

| Zone | Name | % FTP | Watts | Purpose |
|------|------|-------|-------|---------|
| Z1 | Recovery | < 55% | < 145W | Active recovery |
| Z2 | Endurance | 55–75% | 145–197W | Aerobic base, fat oxidation |
| Z3 | Tempo | 76–90% | 200–237W | Muscular endurance |
| Z4 | Threshold | 91–105% | 239–276W | FTP improvement |
| Z5 | VO2max | 106–120% | 279–316W | Max aerobic power |
| Z6 | Anaerobic | > 120% | > 316W | Short power efforts |

### Heart Rate Zones (based on LTHR ~160)

| Zone | HR Range | Feel |
|------|----------|------|
| Z1 | < 130 | Very easy, conversational |
| Z2 | 130–142 | Comfortable, could talk in sentences |
| Z3 | 144–152 | Moderate effort, short sentences |
| Z4 | 153–160 | Hard, few words |
| Z5 | 160–175 | Very hard, no talking |

> **Note on hilly terrain**: In Gijón it's hard to stay in pure Z2 on climbs. On hilly outdoor rides, don't stress about brief Z3 excursions on climbs — focus on *average* power for the ride staying in Z2, let terrain dictate natural variability. Use HR as the primary guide outdoors: stay below 142 bpm on easy days.

---

## 25-Week Periodization Overview

| Phase | Weeks | Dates (approx) | Focus | Weekly Volume |
|-------|-------|-----------------|-------|---------------|
| **Base Rebuild** | 1–4 | Feb 9 – Mar 8 | Aerobic base, re-adaptation, sweet spot intro | 8–12h |
| **Base Build** | 5–8 | Mar 9 – Apr 5 | Volume increase, sweet spot, climbing strength | 10–13h |
| **Build 1** | 9–12 | Apr 6 – May 3 | FTP development, threshold work, longer rides | 12–14h |
| **Build 2** | 13–16 | May 4 – May 31 | Climbing-specific, sustained power, 5-20min efforts | 13–15h |
| **Endurance Specialty** | 17–20 | Jun 1 – Jun 28 | Ultra-endurance simulation, back-to-back long days | 14–18h |
| **Peak / Specificity** | 21–24 | Jun 29 – Jul 26 | Event simulation, pacing practice, mental prep | 13–15h |
| **Taper** | 25 | Jul 27 – Aug 2 | Volume reduction, maintain intensity, freshness | 7–8h |

> Every 4th week is a **recovery week** (~60-65% of previous week's volume, reduced intensity).

---

## Weekly Structure Template

| Day | Session | Type | Notes |
|-----|---------|------|-------|
| **Monday** | Strength AM + Easy spin PM | Strength + Z1-Z2 | Legs focus AM; 30-45min easy spin to flush |
| **Tuesday** | Structured indoor (Rouvy) | Intervals | Key session #1 — sweet spot / threshold |
| **Wednesday** | Easy outdoor ride OR rest | Z2 / Off | Weather dependent; listen to body |
| **Thursday** | Structured indoor (Rouvy) | Intervals | Key session #2 — VO2max / climbing repeats |
| **Friday** | REST | Off | Full rest day — no training |
| **Saturday** | Long outdoor ride | Z2 + terrain | Key session #3 — main endurance builder |
| **Sunday** | Moderate outdoor ride + Strength | Z2-Z3 + Strength PM | Endurance with some tempo on climbs; strength PM |

> This is flexible — swap days based on weather (move outdoor rides to best weather days). The 2 key indoor sessions and 1 long ride are the non-negotiables each week.

---

## Strength Training

Focus on cycling-specific exercises. 2x per week, 30-40 minutes.

**Core exercises** (pick 4-5 per session):
- Single-leg squats or Bulgarian split squats: 3×8-10
- Romanian deadlifts: 3×8-10
- Step-ups (weighted): 3×10 each leg
- Plank variations: 3×45-60s
- Hip bridges / glute bridges: 3×12
- Calf raises: 3×15

**Progression**: Start with bodyweight/light weights in Base phase → add load through Build phases → maintain in Peak/Taper.

> Strength supports climbing and injury prevention for a 2500km event. Keep sessions short and focused — don't create excessive fatigue that compromises cycling.

---

## Progress Tracking (No Formal Tests)

Instead of dedicated FTP tests, track progress through training data:

1. **Indoor benchmarks**: Note average power on similar Rouvy workouts over time — if the same intervals feel easier or power creeps up, fitness is improving.
2. **Outdoor climb repeats**: Pick 1-2 local climbs (10-20 min) and ride them periodically at hard effort. Compare times/power.
3. **Weekly metrics to log**:
   - Total ride time and TSS (or equivalent)
   - Longest ride duration
   - How hard the key sessions felt (RPE 1-10)
   - Resting HR trend (morning)
   - Sleep quality and general fatigue
4. **FTP auto-detection**: Let Intervals.icu or Rouvy estimate FTP from your training data. Update zones when FTP changes by ≥5W.

---

## Weekly Feedback Format

At the end of each week, note:

```
Week #: [number]
Total hours: [actual]
Planned vs actual: [completed all / missed X sessions]
Key session RPE: Tue [1-10], Thu [1-10], Sat [1-10]
Fatigue level (Mon morning): [1-10]
Notable: [anything unusual — illness, soreness, great ride, bad sleep, etc.]
FTP update needed? [yes/no]
```

Based on feedback, I'll adjust the next week: more rest if fatigued, more intensity if feeling strong, or restructure if schedule changed.

---

## Intervals.icu Workout Format Reference

Workouts are written in [Intervals.icu workout text format](https://forum.intervals.icu/t/workout-builder/1163). See `plan/intervals_format.md` for full reference.

```
- 10m 50%          warm-up at 50% FTP
- 3x               repeat 3 times
  - 5m 100%        work interval at FTP
  - 3m 55%         recovery
- 5m 50%           cool-down
```

**Duration units**: `s` = seconds, `m` = minutes, `h` = hours (e.g. `30s`, `10m`, `1h30m`). Do NOT use `min` — it won't generate proper workout steps.

Percentages are of FTP. These can be pasted directly into Intervals.icu workout builder or synced to Rouvy.