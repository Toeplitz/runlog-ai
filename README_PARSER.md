# Coros Running Data Parser

This tool parses Coros running watch data exports (FIT, TCX, and CSV files) and converts them into comprehensive JSON files suitable for AI training analysis.

## Features

- **Multi-format parsing**: Handles FIT, TCX, and CSV files
- **Comprehensive data extraction**:
  - Split-by-split performance metrics (pace, HR, cadence, stride length)
  - GPS trackpoints with coordinates, altitude, speed, heart rate
  - Lap summaries and session data
  - Environmental data (temperature, elevation gain/loss)
  - Physiological metrics (heart rate zones, cadence patterns)

## Installation

```bash
# Required for FIT file parsing (most complete data)
pip install fitparse
```

## Usage

### Parse all activities

```bash
python3 parse_coros_data.py
```

This will:
- Scan all folders in `./data/YYYYMMDD/`
- Parse FIT, TCX, and CSV files found in each folder
- Create JSON files in `./parsed_data/` with the same date names

### Parse a specific date

```bash
python3 parse_coros_data.py --single-date 20251202
```

### Custom directories

```bash
python3 parse_coros_data.py --data-dir /path/to/data --output-dir /path/to/output
```

## Output Format

Each JSON file contains:

```json
{
  "date": "20251202",
  "parsed_at": "2026-01-20T08:29:14.882054",
  "sources": {
    "csv": {
      "file": "473703254759342081.csv",
      "data": {
        "splits": [
          {
            "split": "1",
            "time": "00:03:00",
            "getdistance": 0.29,
            "avg_pace": "00:10:23",
            "avg_hr": 93,
            "avg_run_cadence": 57,
            "avg_stride_length": 84,
            "elevation_gain": 0.0,
            "calories": 15
          }
        ],
        "summary": {
          "getdistance": 4.88,
          "time": "00:35:00",
          "avg_pace": "00:07:10",
          "avg_hr": 135
        }
      }
    },
    "tcx": {
      "file": "473703254759342081.tcx",
      "data": {
        "activity_type": "Running",
        "activity_id": "2025-12-02T12:42:40Z",
        "laps": [...],
        "trackpoints": [
          {
            "time": "2025-12-02T12:42:40Z",
            "position": {"lat": 58.8811639, "lon": 5.6629392},
            "altitude_m": 14.0,
            "distance_m": 7.0,
            "heart_rate": 85,
            "speed_ms": 4.93
          }
        ]
      }
    },
    "fit": {
      "file": "473703254759342081.fit",
      "data": {
        "records": [...],
        "laps": [...],
        "session": {...}
      }
    }
  }
}
```

## Data Available for AI Analysis

The parsed JSON files provide comprehensive training data:

### Performance Metrics
- Distance, time, pace (average, moving, best)
- Split-by-split breakdown
- Cadence (avg, max per split)
- Stride length

### Physiological Data
- Heart rate (avg, max per split)
- Heart rate throughout the run (second-by-second from trackpoints)
- Calories burned

### Environmental Context
- Temperature
- Elevation gain/loss per split
- GPS coordinates and altitude profile

### Detailed Trackpoints
- Second-by-second GPS coordinates
- Continuous heart rate monitoring
- Speed variations
- Altitude changes

## Using with AI Training Coach

The JSON format is designed to be easily parsed by LLMs for training analysis:

1. **Pattern Recognition**: Multiple runs can be compared to identify trends
2. **Performance Analysis**: Split times, heart rate zones, cadence patterns
3. **Recovery Assessment**: Heart rate recovery, pace consistency
4. **Environmental Impact**: Temperature and elevation effects on performance
5. **Training Load**: Distance, intensity, and frequency patterns

## Example: View Data Summary

```bash
python3 view_training_data.py
```

This will show a summary of all your parsed training sessions.
