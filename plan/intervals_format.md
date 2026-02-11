# Intervals.icu Workout Text Format Reference

Reference for writing structured workouts in [Intervals.icu text format](https://forum.intervals.icu/t/workout-builder/1163).

## Duration Units

| Unit | Meaning | Example |
|------|---------|---------|
| `s` | seconds | `30s` |
| `m` | minutes | `10m` |
| `h` | hours | `1h` |
| combined | hours + minutes | `1h30m` |

**Do NOT use `min`** — it displays as text but does not generate structured workout steps or a power chart.

## Intensity Formats

| Format | Example | Meaning |
|--------|---------|---------|
| FTP % | `88%` | 88% of FTP |
| FTP % range | `88-93%` | range of FTP |
| Absolute watts | `200w` | fixed 200 watts |
| Watts range | `180-220w` | watts range |
| Ramp | `Ramp 60-80%` | gradual increase |
| Heart rate | `60% HR` or `100% LTHR` | % of max HR or LTHR |
| Zone | `Z2` or `Z3 HR` | power or HR zone |

## Cadence (optional)

Append RPM target: `- 10m 88% 85-95rpm`

## Structure

```
- [label] [duration] [intensity] [cadence]
```

Steps use `- ` prefix. Indented steps under a repeat block use `  - ` (two spaces).

## Repeats

```
- 3x
  - 5m 100%
  - 3m 55%
```

The `Nx` line starts the repeat. Indented lines below are the repeated steps.

## Complete Example

```
- Warmup 10m 55%
- 3x
  - Work 6m 88% 85-95rpm
  - Recovery 4m 55%
- 5m 55%
- 2x
  - Work 4m 90%
  - Recovery 3m 55%
- Cooldown 5m 50%
```

## Labels (optional)

You can add a label before the duration. Labels are displayed in the workout view but don't affect the structure:

```
- Warmup 10m 55%
- Threshold 5m 100%
- Cooldown 5m 50%
```

## Tips

- Keep recovery intervals at 50-55% for proper rest
- Use `30s` for short sprints, not `0.5m`
- Intervals.icu automatically calculates TSS, duration, and zone distribution
- Paste workout text into the `description` field when creating events via API
- The API parses `description` into structured `workout_doc` with steps and power chart
