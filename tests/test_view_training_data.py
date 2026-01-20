"""
Tests for view_training_data.py module.
"""

import pytest
import json
from pathlib import Path
from view_training_data import (
    parse_time_to_seconds,
    format_pace,
    summarize_activity,
    main
)


class TestParseTimeToSeconds:
    """Tests for parse_time_to_seconds function."""

    def test_parse_hhmmss_format(self):
        """Test parsing HH:MM:SS format."""
        assert parse_time_to_seconds("01:30:45") == 5445  # 1*3600 + 30*60 + 45
        assert parse_time_to_seconds("00:07:10") == 430   # 7*60 + 10
        assert parse_time_to_seconds("02:00:00") == 7200  # 2*3600

    def test_parse_mmss_format(self):
        """Test parsing MM:SS format."""
        assert parse_time_to_seconds("07:10") == 430   # 7*60 + 10
        assert parse_time_to_seconds("25:30") == 1530  # 25*60 + 30

    def test_parse_invalid_format(self):
        """Test parsing invalid time formats."""
        assert parse_time_to_seconds("invalid") is None
        assert parse_time_to_seconds("25") is None
        assert parse_time_to_seconds("") == 0
        assert parse_time_to_seconds("N/A") == 0
        assert parse_time_to_seconds(None) == 0

    def test_parse_with_whitespace(self):
        """Test parsing time with whitespace."""
        assert parse_time_to_seconds("  01:30:45  ") == 5445
        assert parse_time_to_seconds("00:07:10 ") == 430


class TestFormatPace:
    """Tests for format_pace function."""

    def test_format_pace_with_value(self):
        """Test formatting pace with valid value."""
        assert format_pace("00:07:10") == "00:07:10"
        assert format_pace("  00:07:10  ") == "00:07:10"

    def test_format_pace_with_none(self):
        """Test formatting pace with None."""
        assert format_pace(None) == "N/A"

    def test_format_pace_with_empty_string(self):
        """Test formatting pace with empty string."""
        assert format_pace("") == "N/A"


class TestSummarizeActivity:
    """Tests for summarize_activity function."""

    def test_summarize_activity_with_full_data(self, temp_parsed_dir, sample_parsed_activity, capsys):
        """Test summarizing activity with complete data."""
        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(sample_parsed_activity, f)

        summarize_activity(activity_file)

        captured = capsys.readouterr()
        assert "Date: 20251202" in captured.out
        assert "Test Morning Run" in captured.out
        assert "outdoor" in captured.out
        assert "SUMMARY" in captured.out
        assert "SPLITS" in captured.out

    def test_summarize_activity_without_metadata(self, temp_parsed_dir, capsys):
        """Test summarizing activity without metadata."""
        activity = {
            "date": "20251202",
            "metadata": {},
            "sources": {
                "csv": {
                    "data": {
                        "summary": {
                            "getdistance": 5.0,
                            "time": "00:35:00",
                            "avg_pace": "00:07:00"
                        }
                    }
                }
            }
        }

        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(activity, f)

        summarize_activity(activity_file)

        captured = capsys.readouterr()
        assert "Date: 20251202" in captured.out
        assert "SUMMARY" in captured.out
        assert "5.0 km" in captured.out

    def test_summarize_activity_with_splits(self, temp_parsed_dir, capsys):
        """Test summarizing activity with splits data."""
        activity = {
            "date": "20251202",
            "metadata": {},
            "sources": {
                "csv": {
                    "data": {
                        "summary": {"getdistance": 3.0},
                        "splits": [
                            {
                                "split": "1",
                                "getdistance": 1.0,
                                "time": "00:07:00",
                                "avg_pace": "00:07:00",
                                "avg_hr": 135,
                                "avg_run_cadence": 170,
                                "elevation_gain": 5
                            },
                            {
                                "split": "2",
                                "getdistance": 1.0,
                                "time": "00:07:10",
                                "avg_pace": "00:07:10",
                                "avg_hr": 138,
                                "avg_run_cadence": 172,
                                "elevation_gain": 3
                            }
                        ]
                    }
                }
            }
        }

        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(activity, f)

        summarize_activity(activity_file)

        captured = capsys.readouterr()
        assert "SPLITS (2 total)" in captured.out
        assert "00:07:00" in captured.out
        assert "00:07:10" in captured.out

    def test_summarize_activity_with_tcx_data(self, temp_parsed_dir, capsys):
        """Test summarizing activity with TCX data."""
        activity = {
            "date": "20251202",
            "metadata": {},
            "sources": {
                "tcx": {
                    "data": {
                        "activity_type": "Running",
                        "activity_id": "2025-12-02T12:00:00Z",
                        "laps": [{"start_time": "2025-12-02T12:00:00Z"}],
                        "trackpoints": [
                            {
                                "time": "2025-12-02T12:00:00Z",
                                "position": {"lat": 58.881234, "lon": 5.663456}
                            },
                            {
                                "time": "2025-12-02T12:00:01Z",
                                "position": {"lat": 58.881244, "lon": 5.663466}
                            }
                        ]
                    }
                }
            }
        }

        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(activity, f)

        summarize_activity(activity_file)

        captured = capsys.readouterr()
        assert "TCX DATA" in captured.out
        assert "Running" in captured.out
        assert "2 GPS points" in captured.out
        assert "58.881234" in captured.out
        assert "Start Position" in captured.out
        assert "End Position" in captured.out

    def test_summarize_activity_with_fit_data(self, temp_parsed_dir, capsys):
        """Test summarizing activity with FIT data."""
        activity = {
            "date": "20251202",
            "metadata": {},
            "sources": {
                "fit": {
                    "data": {
                        "records": [{"timestamp": "2025-12-02T12:00:00Z"}] * 100,
                        "laps": [{"start_time": "2025-12-02T12:00:00Z"}],
                        "session": {"sport": "running", "total_distance": 5000}
                    }
                }
            }
        }

        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(activity, f)

        summarize_activity(activity_file)

        captured = capsys.readouterr()
        assert "FIT DATA" in captured.out
        assert "Records:         100" in captured.out
        assert "Laps:            1" in captured.out
        assert "Session Data:    2 fields" in captured.out

    def test_summarize_activity_with_fit_error(self, temp_parsed_dir, capsys):
        """Test summarizing activity when FIT parsing failed."""
        activity = {
            "date": "20251202",
            "metadata": {},
            "sources": {
                "fit": {
                    "data": {
                        "error": "Failed to parse FIT file"
                    }
                }
            }
        }

        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(activity, f)

        summarize_activity(activity_file)

        captured = capsys.readouterr()
        # FIT DATA section should not appear
        assert "FIT DATA" not in captured.out

    def test_summarize_activity_with_metadata_error(self, temp_parsed_dir, capsys):
        """Test summarizing activity with metadata error."""
        activity = {
            "date": "20251202",
            "metadata": {"error": "Failed to read metadata"},
            "sources": {}
        }

        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(activity, f)

        summarize_activity(activity_file)

        captured = capsys.readouterr()
        assert "Date: 20251202" in captured.out
        # Metadata section should not appear due to error
        assert "METADATA" not in captured.out


class TestMainFunction:
    """Tests for the main function and CLI."""

    def test_main_list_activities(self, temp_parsed_dir, sample_parsed_activity, monkeypatch, capsys):
        """Test main function with --list flag."""
        import sys

        # Create activity files
        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(sample_parsed_activity, f)

        monkeypatch.setattr(sys, "argv", [
            "view_training_data.py",
            "--dir", str(temp_parsed_dir),
            "--list"
        ])

        main()

        captured = capsys.readouterr()
        assert "Found 1 activities" in captured.out
        assert "20251202" in captured.out
        assert "2.0 km" in captured.out

    def test_main_view_specific_date(self, temp_parsed_dir, sample_parsed_activity, monkeypatch, capsys):
        """Test main function with --date flag."""
        import sys

        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(sample_parsed_activity, f)

        monkeypatch.setattr(sys, "argv", [
            "view_training_data.py",
            "--dir", str(temp_parsed_dir),
            "--date", "20251202"
        ])

        main()

        captured = capsys.readouterr()
        assert "Date: 20251202" in captured.out
        assert "Test Morning Run" in captured.out

    def test_main_view_nonexistent_date(self, temp_parsed_dir, monkeypatch, capsys):
        """Test main function with non-existent date."""
        import sys
        import json

        # Create a dummy activity so the directory isn't empty
        activity = {
            "date": "20251201",
            "metadata": {},
            "sources": {}
        }
        activity_file = temp_parsed_dir / "20251201.json"
        with open(activity_file, 'w') as f:
            json.dump(activity, f)

        monkeypatch.setattr(sys, "argv", [
            "view_training_data.py",
            "--dir", str(temp_parsed_dir),
            "--date", "20991231"
        ])

        main()

        captured = capsys.readouterr()
        assert "does not exist" in captured.out

    def test_main_view_all_activities(self, temp_parsed_dir, monkeypatch, capsys):
        """Test main function viewing all activities."""
        import sys

        # Create multiple activities
        activities = [
            {
                "date": "20251201",
                "metadata": {"title": "Run 1"},
                "sources": {
                    "csv": {
                        "data": {
                            "summary": {"getdistance": 5.0}
                        }
                    }
                }
            },
            {
                "date": "20251202",
                "metadata": {"title": "Run 2"},
                "sources": {
                    "csv": {
                        "data": {
                            "summary": {"getdistance": 3.0}
                        }
                    }
                }
            }
        ]

        for activity in activities:
            activity_file = temp_parsed_dir / f"{activity['date']}.json"
            with open(activity_file, 'w') as f:
                json.dump(activity, f)

        monkeypatch.setattr(sys, "argv", [
            "view_training_data.py",
            "--dir", str(temp_parsed_dir)
        ])

        main()

        captured = capsys.readouterr()
        assert "Date: 20251201" in captured.out
        assert "Date: 20251202" in captured.out
        assert "Run 1" in captured.out
        assert "Run 2" in captured.out

    def test_main_nonexistent_directory(self, temp_parsed_dir, monkeypatch, capsys):
        """Test main function with non-existent directory."""
        import sys

        nonexistent_dir = temp_parsed_dir / "nonexistent"

        monkeypatch.setattr(sys, "argv", [
            "view_training_data.py",
            "--dir", str(nonexistent_dir)
        ])

        main()

        captured = capsys.readouterr()
        assert "does not exist" in captured.out
        assert "Run parse_coros_data.py first" in captured.out

    def test_main_empty_directory(self, temp_parsed_dir, monkeypatch, capsys):
        """Test main function with empty directory."""
        import sys

        monkeypatch.setattr(sys, "argv", [
            "view_training_data.py",
            "--dir", str(temp_parsed_dir)
        ])

        main()

        captured = capsys.readouterr()
        assert "No JSON files found" in captured.out

    def test_main_list_with_missing_summary_data(self, temp_parsed_dir, monkeypatch, capsys):
        """Test --list with activity missing summary data."""
        import sys

        activity = {
            "date": "20251202",
            "metadata": {},
            "sources": {}
        }

        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(activity, f)

        monkeypatch.setattr(sys, "argv", [
            "view_training_data.py",
            "--dir", str(temp_parsed_dir),
            "--list"
        ])

        main()

        captured = capsys.readouterr()
        assert "20251202" in captured.out
        assert "N/A" in captured.out  # Should show N/A for missing data
