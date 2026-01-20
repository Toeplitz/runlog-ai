# Quick Start Guide - Coros Training Data Parser

## Step 0: Add Metadata (Optional but Recommended)

Each activity folder should contain a `metadata.json` file with additional context:

```bash
# Copy template to new activity folder
cp metadata_template.json data/20251202/metadata.json
```

Edit the file to add details:
```json
{
  "run_type": "outdoor",
  "title": "Morning easy run",
  "notes": "Felt strong, good weather",
  "workout_type": "easy run",
  "perceived_effort": "6/10"
}
```

Fields you can use:
- `run_type`: "outdoor" or "indoor" (treadmill)
- `title`: Short descriptive title for the workout
- `notes`: Any observations about the run
- `workout_type`: "easy", "tempo", "intervals", "long run", etc.
- `perceived_effort`: Your subjective effort level
- `weather`: Weather conditions
- `route`: Route name or description

## Step 1: Parse Your Training Data

Convert all Coros exports to JSON format:

```bash
python3 parse_coros_data.py
```

This will:
- Scan `./data/YYYYMMDD/` folders
- Read `metadata.json` files if present
- Parse FIT, TCX, and CSV files
- Create JSON files in `./parsed_data/`

## Step 2: View Your Training Data

### List all activities
```bash
python3 view_training_data.py --list
```

### View detailed summary for a specific date
```bash
python3 view_training_data.py --date 20251206
```

### View all activities
```bash
python3 view_training_data.py
```

## Step 3: Create Training Log for AI Analysis

Aggregate all activities into a single file:

```bash
python3 create_training_log.py
```

This creates `training_log.json` with:
- All your activities
- Aggregated statistics
- Optimized format for AI analysis

## Working with AI Training Coach

You can provide the AI with:

1. **Individual activity**: `parsed_data/20251206.json`
   - For analyzing specific workouts
   - Detailed split analysis
   - GPS route review

2. **Training log**: `training_log.json`
   - For overall training pattern analysis
   - Progress tracking over time
   - Volume and intensity trends

3. **Custom queries**: The AI can analyze:
   - "Am I improving my pace?"
   - "What's my heart rate trend?"
   - "Are my splits consistent?"
   - "How does temperature affect my performance?"
   - "What's my optimal cadence?"

## Example AI Prompts

**For single workout analysis:**
```
Here's my run from 2025-12-06. Can you analyze my pacing strategy
and heart rate response? [attach 20251206.json]
```

**For training pattern analysis:**
```
Review my last 3 runs. Am I building volume appropriately?
What should my next workout focus on? [attach training_log.json]
```

**For specific metrics:**
```
Looking at my heart rate data across these runs, am I seeing
signs of improved cardiovascular fitness? [attach training_log.json]
```

## File Structure

```
loping/
├── data/
│   ├── 20251202/
│   │   ├── *.fit
│   │   ├── *.tcx
│   │   └── *.csv
│   ├── 20251204/
│   └── 20251206/
├── parsed_data/
│   ├── 20251202.json  (individual activity files)
│   ├── 20251204.json
│   └── 20251206.json
├── training_log.json  (consolidated file)
├── parse_coros_data.py
├── view_training_data.py
└── create_training_log.py
```

## Key Metrics Available

Each parsed activity includes:

**Performance:**
- Distance, time, pace (average, moving, best)
- Split-by-split breakdown
- Calories burned

**Physiological:**
- Heart rate (average, max, per split, per second)
- Cadence (average, max)
- Stride length

**Environmental:**
- Temperature
- Elevation gain/loss
- GPS coordinates and altitude

**Detailed Tracking:**
- Second-by-second GPS trackpoints
- Continuous heart rate monitoring
- Speed and altitude variations

## Tips

1. Keep your `data/` folder organized with one folder per activity date
2. Re-run the parser when you add new activities
3. The training log file is perfect for sharing with AI coaches
4. Individual JSON files are better for deep-dive analysis of specific workouts
5. GPS trackpoints are limited to 10,000 points per activity to keep files manageable

## Need Help?

- Check `README_PARSER.md` for detailed documentation
- All scripts support `--help` flag for options
- JSON files are human-readable for manual inspection
