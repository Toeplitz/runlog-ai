# Metadata Guide

## Overview

Each activity folder in `data/YYYYMMDD/` can contain a `metadata.json` file to provide additional context about your training sessions. This metadata helps AI training coaches better understand your workouts beyond just the numbers.

## File Location

```
data/
├── 20251202/
│   ├── metadata.json         ← Add this file
│   ├── *.fit
│   ├── *.tcx
│   └── *.csv
```

## Creating Metadata Files

### For New Activities

When you add a new activity to the `data/` folder:

```bash
# Copy the template
cp metadata_template.json data/20260120/metadata.json

# Edit the file
nano data/20260120/metadata.json  # or use your preferred editor
```

### Batch Creation

To add metadata files to multiple activities at once:

```bash
for dir in data/*/; do
  if [ ! -f "${dir}metadata.json" ]; then
    cp metadata_template.json "${dir}metadata.json"
    echo "Created ${dir}metadata.json"
  fi
done
```

## Metadata Fields

### Required Fields

**`run_type`** (string)
- Values: `"outdoor"` or `"indoor"`
- Indicates whether the run was outside or on a treadmill
- Example: `"run_type": "outdoor"`

### Optional Fields

**`title`** (string)
- Short descriptive title for the workout
- Displayed prominently in activity summaries
- Examples:
  - `"Easy running 20min"`
  - `"Tempo run 5K"`
  - `"Morning recovery jog"`
  - `"Hill repeats session"`
  - `"Race day - 10K"`

**`notes`** (string)
- Free-form text for observations about the run
- Examples:
  - `"Felt strong, good weather"`
  - `"Legs tired from yesterday's workout"`
  - `"First run after recovery week"`

**`workout_type`** (string)
- Category of workout
- Suggested values:
  - `"easy"` - Easy/recovery run
  - `"tempo"` - Tempo/threshold run
  - `"intervals"` - Interval training
  - `"long run"` - Long distance run
  - `"race"` - Race effort
  - `"fartlek"` - Fartlek/speed play
  - `"progression"` - Progressive run
- Example: `"workout_type": "tempo"`

**`perceived_effort`** (string)
- Your subjective effort level
- Suggested format: `"7/10"` or `"hard"` or `"moderate"`
- Examples:
  - `"6/10"`
  - `"easy"`
  - `"very hard"`

**`weather`** (string)
- Weather conditions during the run
- Examples:
  - `"Sunny, 15°C"`
  - `"Light rain, windy"`
  - `"Cold, below freezing"`

**`route`** (string)
- Route name or description
- Examples:
  - `"Park loop"`
  - `"Hill route"`
  - `"Coastal path"`

### Custom Fields

You can add any custom fields that are relevant to your training:

```json
{
  "run_type": "outdoor",
  "notes": "Testing new shoes",
  "workout_type": "easy",
  "equipment": "Nike Pegasus 40",
  "running_partner": "Training group",
  "pre_run_meal": "Banana 30min before",
  "post_run_feeling": "Great, no soreness"
}
```

## Example Metadata Files

### Simple Outdoor Run
```json
{
  "run_type": "outdoor",
  "title": "",
  "notes": ""
}
```

### Detailed Tempo Run
```json
{
  "run_type": "outdoor",
  "title": "River path tempo run",
  "notes": "Felt strong throughout. Good progression in final km.",
  "workout_type": "tempo",
  "perceived_effort": "8/10",
  "weather": "Cool, 12°C, slight wind",
  "route": "River path tempo loop"
}
```

### Treadmill Interval Session
```json
{
  "run_type": "indoor",
  "title": "6x800m intervals",
  "notes": "6x800m intervals with 90s rest. Hit all targets.",
  "workout_type": "intervals",
  "perceived_effort": "9/10",
  "equipment": "Gym treadmill"
}
```

### Race Day
```json
{
  "run_type": "outdoor",
  "title": "Local 10K race - New PR!",
  "notes": "Local 10K race. New PR! Felt great in the final 2km.",
  "workout_type": "race",
  "perceived_effort": "10/10",
  "weather": "Perfect conditions, 10°C, no wind",
  "route": "Town center 10K course"
}
```

## How Metadata is Used

### In Parsed JSON Files
The metadata appears in each activity's JSON file:

```json
{
  "date": "20251202",
  "parsed_at": "2026-01-20T08:29:14.882054",
  "metadata": {
    "run_type": "outdoor",
    "title": "Morning easy run",
    "notes": "Felt strong today",
    "workout_type": "easy"
  },
  "sources": { ... }
}
```

### In Training Log
The aggregated training log includes metadata for each activity:

```json
{
  "activities": [
    {
      "date": "20251202",
      "metadata": {
        "run_type": "outdoor",
        "title": "Morning easy run",
        "workout_type": "easy"
      },
      "summary": { ... }
    }
  ]
}
```

### In View Script
When viewing activities, metadata is displayed:

```
================================================================================
Date: 20251202
Title: Morning easy run
================================================================================

METADATA
--------------------------------------------------------------------------------
  Run Type:        outdoor
  Title:           Morning easy run
  Notes:           Felt strong today

SUMMARY
--------------------------------------------------------------------------------
  Distance:        4.88 km
  ...
```

## Benefits for AI Analysis

Rich metadata helps AI training coaches:

1. **Understand context** - Why was a run slower or faster than usual?
2. **Track training types** - Are you balancing easy runs with hard workouts?
3. **Identify patterns** - How does weather affect your performance?
4. **Assess recovery** - Do your notes indicate fatigue or freshness?
5. **Evaluate progression** - How has perceived effort changed for similar paces?
6. **Provide recommendations** - Suggest workouts based on your training history

## Tips

1. **Be consistent** - Use similar terminology across activities
2. **Be honest** - Accurate perceived effort helps AI understand your fitness
3. **Add notes promptly** - Record observations while fresh in your mind
4. **Start simple** - Just `run_type` is fine; add more fields as needed
5. **Review periodically** - Look back at notes to see patterns you might have missed

## Editing Existing Metadata

To update metadata for an existing activity:

```bash
# Edit the file
nano data/20251202/metadata.json

# Re-run the parser
python3 parse_coros_data.py

# Regenerate training log
python3 create_training_log.py
```

The parser will pick up the updated metadata on the next run.
