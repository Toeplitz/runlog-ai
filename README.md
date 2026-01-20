# runlog-ai

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/toeplitz/runlog-ai/workflows/Tests/badge.svg)](https://github.com/toeplitz/runlog-ai/actions)
[![codecov](https://codecov.io/gh/toeplitz/runlog-ai/branch/main/graph/badge.svg)](https://codecov.io/gh/toeplitz/runlog-ai)

> Transform your running watch data into AI-ready training insights

A Python toolkit for parsing and analyzing running watch data exports (Coros, Garmin, and other FIT/TCX formats). Convert FIT, TCX, and CSV files into structured JSON format optimized for AI training analysis and personal insights.

## Features

- **Multi-format parsing**: Handles FIT, TCX, and CSV exports from Coros watches
- **Comprehensive data extraction**:
  - Split-by-split performance metrics (pace, HR, cadence, stride length)
  - Second-by-second GPS trackpoints with coordinates, altitude, and speed
  - Heart rate monitoring and trends
  - Environmental data (temperature, elevation gain/loss)
- **Metadata support**: Add custom context to runs (workout type, perceived effort, notes)
- **AI-ready output**: Clean JSON format perfect for feeding to AI training coaches
- **Training log aggregation**: Combine multiple activities for pattern analysis
- **Interactive viewing**: CLI tools to explore your training data

## Installation

### Quick Install

```bash
git clone https://github.com/toeplitz/runlog-ai.git
cd runlog-ai
pip install -r requirements.txt
```

### Manual Install

```bash
# Required for FIT file parsing
pip install fitparse
```

## Quick Start

### 1. Export Your Data from Coros

1. Open the Coros app
2. Go to your activity
3. Export as FIT, TCX, and CSV files
4. Create a folder structure: `data/YYYYMMDD/` for each activity
5. Place the exported files in the corresponding date folder

Example structure:
```
data/
├── 20251202/
│   ├── metadata.json
│   ├── activity.fit
│   ├── activity.tcx
│   └── activity.csv
└── 20251204/
    ├── metadata.json
    ├── activity.fit
    ├── activity.tcx
    └── activity.csv
```

### 2. Add Metadata (Optional but Recommended)

Create a `metadata.json` file in each activity folder:

```bash
cp metadata_template.json data/20251202/metadata.json
```

Edit with your details:
```json
{
  "run_type": "outdoor",
  "title": "Morning tempo run",
  "notes": "Felt strong, good weather",
  "workout_type": "tempo",
  "perceived_effort": "8/10"
}
```

### 3. Parse Your Data

```bash
python3 parse_coros_data.py
```

This creates JSON files in `parsed_data/` with all your training metrics.

### 4. View Your Training Data

```bash
# List all activities
python3 view_training_data.py --list

# View detailed summary
python3 view_training_data.py --date 20251202

# View all activities
python3 view_training_data.py
```

### 5. Create Training Log for AI Analysis

```bash
# Default: Creates chunks of 5 activities each in training_log_chunks/ folder
python3 create_training_log.py
```

By default, this **automatically chunks** your training log into manageable files (5 activities per chunk) stored in the `training_log_chunks/` folder. Each chunk is ~5-10 MB, perfect for uploading to ChatGPT and other AI tools.

#### Output Files (Default Behavior)

The `training_log_chunks/` folder will contain:
- `training_log_part1.json` - First 5 activities
- `training_log_part2.json` - Next 5 activities
- `training_log_part3.json` - Next 5 activities
- ...and so on
- `training_log_index.json` - Overview of all chunks with statistics

#### Customizing Chunking

```bash
# Disable chunking (create single large file)
python3 create_training_log.py --chunk-size 0

# Use different chunk size
python3 create_training_log.py --chunk-size 10

# Custom output directory for chunks
python3 create_training_log.py --chunks-dir my_chunks

# Custom chunk naming pattern
python3 create_training_log.py --chunk-output-pattern "runs_{}.json"
```

Each chunk file is optimized for AI tools and can be uploaded individually. The index file helps you navigate which chunk contains which activities and date ranges.

## Usage Examples

### Parsing a Single Activity

```bash
python3 parse_coros_data.py --single-date 20251202
```

### Custom Directories

```bash
python3 parse_coros_data.py --data-dir /path/to/data --output-dir /path/to/output
```

### Using with AI Training Coaches

The JSON output is optimized for AI analysis. You can:

1. **Upload individual activities** for workout-specific analysis:
   ```
   "Analyze my splits and heart rate from this tempo run"
   [attach parsed_data/20251202.json]
   ```

2. **Upload training log chunks** for comprehensive analysis (recommended):
   ```
   "Analyze my recent training from this chunk"
   [attach training_log_chunks/training_log_part1.json]

   "Compare my training patterns across different periods"
   [attach training_log_chunks/training_log_index.json to see overview]

   "Review my December training and suggest improvements"
   [attach the relevant chunk covering December]
   ```

3. **Ask specific questions**:
   - "Am I building volume too quickly?"
   - "How does my heart rate respond to different paces?"
   - "What's my optimal cadence?"
   - "Do I need more easy runs?"
   - "Based on this chunk, am I ready for a marathon?"

## Output Format

Each parsed activity includes:

```json
{
  "date": "20251202",
  "metadata": {
    "run_type": "outdoor",
    "title": "Morning tempo run",
    "workout_type": "tempo",
    "notes": "Felt strong"
  },
  "sources": {
    "csv": {
      "data": {
        "splits": [...],
        "summary": {
          "getdistance": 4.88,
          "time": "00:35:00",
          "avg_pace": "00:07:10",
          "avg_hr": 135
        }
      }
    },
    "tcx": {
      "data": {
        "trackpoints": [
          {
            "time": "2025-12-02T12:42:40Z",
            "position": {"lat": 58.881, "lon": 5.663},
            "heart_rate": 85,
            "speed_ms": 4.93
          }
        ]
      }
    },
    "fit": {
      "data": {
        "records": [...],
        "laps": [...],
        "session": {...}
      }
    }
  }
}
```

## Available Scripts

| Script | Purpose |
|--------|---------|
| `parse_coros_data.py` | Parse FIT/TCX/CSV files to JSON |
| `view_training_data.py` | View and explore parsed data |
| `create_training_log.py` | Aggregate activities into training log |

## Metadata Fields

Enhance your training data with custom metadata:

| Field | Description | Example |
|-------|-------------|---------|
| `run_type` | Indoor or outdoor | `"outdoor"` |
| `title` | Workout title | `"Morning tempo run"` |
| `notes` | Observations | `"Felt strong, legs fresh"` |
| `workout_type` | Training category | `"tempo"`, `"easy"`, `"intervals"` |
| `perceived_effort` | Subjective difficulty | `"8/10"`, `"hard"` |
| `weather` | Conditions | `"Cool, 12°C, slight wind"` |
| `route` | Route name | `"River path loop"` |

See [METADATA_GUIDE.md](METADATA_GUIDE.md) for complete documentation.

## Documentation

- [Quick Start Guide](QUICK_START.md) - Get started quickly
- [Metadata Guide](METADATA_GUIDE.md) - Complete metadata documentation
- [Parser Documentation](README_PARSER.md) - Technical details

## What Data is Parsed?

### From CSV Files
- Split-by-split metrics (pace, distance, time)
- Heart rate (average, max per split)
- Cadence and stride length
- Elevation gain/loss
- Temperature and calories

### From TCX Files
- Second-by-second GPS coordinates
- Continuous heart rate monitoring
- Altitude and speed variations
- Lap summaries

### From FIT Files
- Most complete raw data from the watch
- All sensor readings
- Session metadata

## Requirements

- Python 3.6+
- `fitparse` (for FIT file parsing)

## Testing

This project includes a comprehensive pytest test suite.

### Running Tests

```bash
# Install test dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_parse_coros_data.py

# Run tests without coverage (faster)
pytest --no-cov
```

### Test Structure

- `tests/test_parse_coros_data.py` - Tests for data parsing (CSV, TCX, FIT)
- `tests/test_create_training_log.py` - Tests for training log aggregation
- `tests/test_view_training_data.py` - Tests for data viewing/display
- `tests/conftest.py` - Shared test fixtures

See [tests/README.md](tests/README.md) for detailed testing documentation.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Quick ways to help:
- Report bugs and suggest features via GitHub Issues
- Improve documentation
- Add support for other watch brands (Garmin, Polar, etc.)
- Enhance AI output format
- Add visualization tools

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Uses [fitparse](https://github.com/dtcooper/python-fitparse) for FIT file parsing
- Inspired by the need for better AI-ready training data formats

## Why runlog-ai?

Most training platforms lock your data in proprietary formats. runlog-ai gives you:

1. **Full data ownership** - Your training data in open, accessible JSON format
2. **AI-ready format** - Perfect for modern AI training coaches
3. **Rich context** - Add notes, perceived effort, and custom metadata
4. **Complete history** - Aggregate all your runs for pattern analysis
5. **Privacy** - Process data locally, share what you want

## Example: AI Training Analysis

```bash
# Parse all your runs
python3 parse_coros_data.py

# Create comprehensive log (automatically chunked)
python3 create_training_log.py

# Files created in training_log_chunks/:
# - training_log_part1.json, training_log_part2.json, etc.
# - training_log_index.json (overview)

# Now you can upload chunks to AI and ask questions like:
# "Based on this chunk, am I ready for a marathon?"
# "What's my optimal easy run pace based on my heart rate data?"
# "Do I show signs of overtraining in this period?"
# "Compare my training intensity across these chunks"
```

## Support

- Report issues: [GitHub Issues](https://github.com/yourusername/runlog-ai/issues)
- Documentation: See docs in this repository
- Examples: Check out [QUICK_START.md](QUICK_START.md)

---
