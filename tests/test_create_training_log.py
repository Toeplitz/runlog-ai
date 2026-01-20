"""
Tests for create_training_log.py module.
"""

import pytest
import json
from pathlib import Path
from create_training_log import aggregate_training_data


class TestAggregateTrainingData:
    """Tests for aggregate_training_data function."""

    def test_aggregate_with_single_activity(self, temp_parsed_dir, sample_parsed_activity):
        """Test aggregating a single activity."""
        # Create a parsed activity file
        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(sample_parsed_activity, f)

        output_file = temp_parsed_dir / "training_log.json"
        aggregate_training_data(str(temp_parsed_dir), str(output_file))

        # Verify output file exists
        assert output_file.exists()

        # Load and verify content
        with open(output_file, 'r') as f:
            training_log = json.load(f)

        assert "metadata" in training_log
        assert "activities" in training_log
        assert training_log["metadata"]["total_activities"] == 1
        assert len(training_log["activities"]) == 1

        # Verify activity data
        activity = training_log["activities"][0]
        assert activity["date"] == "20251202"
        assert activity["metadata"]["run_type"] == "outdoor"
        assert activity["summary"]["getdistance"] == 2.0
        assert activity["summary"]["avg_hr"] == 136

    def test_aggregate_with_multiple_activities(self, temp_parsed_dir):
        """Test aggregating multiple activities."""
        # Create multiple parsed activity files
        activities = [
            {
                "date": "20251201",
                "metadata": {"run_type": "outdoor"},
                "sources": {
                    "csv": {
                        "data": {
                            "summary": {
                                "getdistance": 5.0,
                                "time": "00:35:00",
                                "avg_hr": 140,
                                "calories": 300
                            },
                            "splits": [{"split": "1", "getdistance": 1.0}]
                        }
                    }
                }
            },
            {
                "date": "20251202",
                "metadata": {"run_type": "outdoor"},
                "sources": {
                    "csv": {
                        "data": {
                            "summary": {
                                "getdistance": 3.0,
                                "time": "00:21:00",
                                "avg_hr": 135,
                                "calories": 180
                            },
                            "splits": []
                        }
                    }
                }
            }
        ]

        for activity in activities:
            activity_file = temp_parsed_dir / f"{activity['date']}.json"
            with open(activity_file, 'w') as f:
                json.dump(activity, f)

        output_file = temp_parsed_dir / "training_log.json"
        aggregate_training_data(str(temp_parsed_dir), str(output_file))

        # Load and verify
        with open(output_file, 'r') as f:
            training_log = json.load(f)

        assert training_log["metadata"]["total_activities"] == 2
        assert len(training_log["activities"]) == 2

        # Verify statistics
        stats = training_log["metadata"]["statistics"]
        assert stats["total_distance_km"] == 8.0
        assert stats["total_calories"] == 480
        assert stats["average_distance_per_run"] == 4.0

    def test_aggregate_with_tcx_metadata(self, temp_parsed_dir):
        """Test aggregating with TCX metadata."""
        activity = {
            "date": "20251202",
            "metadata": {},
            "sources": {
                "csv": {
                    "data": {
                        "summary": {"getdistance": 2.0, "time": "00:14:00"}
                    }
                },
                "tcx": {
                    "data": {
                        "activity_type": "Running",
                        "activity_id": "2025-12-02T12:00:00Z",
                        "trackpoints": [{"time": "2025-12-02T12:00:00Z"}],
                        "laps": [{"start_time": "2025-12-02T12:00:00Z"}]
                    }
                }
            }
        }

        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(activity, f)

        output_file = temp_parsed_dir / "training_log.json"
        aggregate_training_data(str(temp_parsed_dir), str(output_file))

        with open(output_file, 'r') as f:
            training_log = json.load(f)

        # Verify TCX metadata is included
        activity_data = training_log["activities"][0]
        assert "tcx_metadata" in activity_data
        assert activity_data["tcx_metadata"]["activity_type"] == "Running"
        assert activity_data["tcx_metadata"]["total_trackpoints"] == 1
        assert activity_data["tcx_metadata"]["total_laps"] == 1

    def test_aggregate_with_missing_csv_data(self, temp_parsed_dir):
        """Test aggregating activity without CSV data."""
        activity = {
            "date": "20251202",
            "metadata": {"run_type": "outdoor"},
            "sources": {
                "tcx": {
                    "data": {
                        "activity_type": "Running"
                    }
                }
            }
        }

        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(activity, f)

        output_file = temp_parsed_dir / "training_log.json"
        aggregate_training_data(str(temp_parsed_dir), str(output_file))

        with open(output_file, 'r') as f:
            training_log = json.load(f)

        # Should still process without errors
        assert len(training_log["activities"]) == 1
        assert "summary" not in training_log["activities"][0]

    def test_aggregate_with_invalid_numeric_values(self, temp_parsed_dir):
        """Test aggregating with invalid numeric values in summary."""
        activity = {
            "date": "20251202",
            "metadata": {},
            "sources": {
                "csv": {
                    "data": {
                        "summary": {
                            "getdistance": "invalid",
                            "time": "invalid:time",
                            "calories": "N/A"
                        }
                    }
                }
            }
        }

        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(activity, f)

        output_file = temp_parsed_dir / "training_log.json"
        aggregate_training_data(str(temp_parsed_dir), str(output_file))

        with open(output_file, 'r') as f:
            training_log = json.load(f)

        # Should handle gracefully with zeros
        stats = training_log["metadata"]["statistics"]
        assert stats["total_distance_km"] == 0
        assert stats["total_calories"] == 0

    def test_aggregate_time_parsing(self, temp_parsed_dir):
        """Test correct parsing of time strings."""
        activities = [
            {
                "date": "20251201",
                "metadata": {},
                "sources": {
                    "csv": {
                        "data": {
                            "summary": {
                                "getdistance": 5.0,
                                "time": "01:30:45",  # 1 hour 30 min 45 sec
                                "calories": 300
                            }
                        }
                    }
                }
            },
            {
                "date": "20251202",
                "metadata": {},
                "sources": {
                    "csv": {
                        "data": {
                            "summary": {
                                "getdistance": 3.0,
                                "time": "00:25:15",  # 25 min 15 sec
                                "calories": 180
                            }
                        }
                    }
                }
            }
        ]

        for activity in activities:
            activity_file = temp_parsed_dir / f"{activity['date']}.json"
            with open(activity_file, 'w') as f:
                json.dump(activity, f)

        output_file = temp_parsed_dir / "training_log.json"
        aggregate_training_data(str(temp_parsed_dir), str(output_file))

        with open(output_file, 'r') as f:
            training_log = json.load(f)

        # Total time should be 1:30:45 + 0:25:15 = 1:56:00
        stats = training_log["metadata"]["statistics"]
        assert stats["total_time_formatted"] == "01:56:00"

    def test_aggregate_date_range(self, temp_parsed_dir):
        """Test date range in statistics."""
        activities = [
            {"date": "20251120", "metadata": {}, "sources": {}},
            {"date": "20251125", "metadata": {}, "sources": {}},
            {"date": "20251201", "metadata": {}, "sources": {}}
        ]

        for activity in activities:
            activity_file = temp_parsed_dir / f"{activity['date']}.json"
            with open(activity_file, 'w') as f:
                json.dump(activity, f)

        output_file = temp_parsed_dir / "training_log.json"
        aggregate_training_data(str(temp_parsed_dir), str(output_file))

        with open(output_file, 'r') as f:
            training_log = json.load(f)

        stats = training_log["metadata"]["statistics"]
        assert stats["date_range"]["first_activity"] == "20251120"
        assert stats["date_range"]["last_activity"] == "20251201"

    def test_aggregate_nonexistent_directory(self, temp_parsed_dir, capsys):
        """Test with non-existent directory."""
        nonexistent_dir = temp_parsed_dir / "nonexistent"
        output_file = temp_parsed_dir / "training_log.json"

        aggregate_training_data(str(nonexistent_dir), str(output_file))

        captured = capsys.readouterr()
        assert "does not exist" in captured.out

        # Output file should not be created
        assert not output_file.exists()

    def test_aggregate_empty_directory(self, temp_parsed_dir, capsys):
        """Test with empty directory (no JSON files)."""
        output_file = temp_parsed_dir / "training_log.json"
        aggregate_training_data(str(temp_parsed_dir), str(output_file))

        captured = capsys.readouterr()
        assert "No JSON files found" in captured.out

        # Output file should not be created
        assert not output_file.exists()

    def test_aggregate_splits_included(self, temp_parsed_dir):
        """Test that splits are included in activity summary."""
        activity = {
            "date": "20251202",
            "metadata": {},
            "sources": {
                "csv": {
                    "data": {
                        "summary": {"getdistance": 3.0},
                        "splits": [
                            {"split": "1", "getdistance": 1.0, "time": "00:07:00"},
                            {"split": "2", "getdistance": 1.0, "time": "00:07:10"},
                            {"split": "3", "getdistance": 1.0, "time": "00:07:20"}
                        ]
                    }
                }
            }
        }

        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(activity, f)

        output_file = temp_parsed_dir / "training_log.json"
        aggregate_training_data(str(temp_parsed_dir), str(output_file))

        with open(output_file, 'r') as f:
            training_log = json.load(f)

        activity_data = training_log["activities"][0]
        assert "splits" in activity_data
        assert len(activity_data["splits"]) == 3
        assert activity_data["splits"][0]["split"] == "1"


class TestMainFunction:
    """Tests for the main function and CLI."""

    def test_main_default_arguments(self, temp_parsed_dir, sample_parsed_activity, monkeypatch):
        """Test main function with default arguments."""
        import sys
        from create_training_log import main

        # Create a parsed activity file
        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(sample_parsed_activity, f)

        # Change to temp directory and run
        monkeypatch.chdir(temp_parsed_dir.parent)
        monkeypatch.setattr(sys, "argv", [
            "create_training_log.py",
            "--input-dir", str(temp_parsed_dir)
        ])

        main()

        # Check output file was created
        output_file = temp_parsed_dir.parent / "training_log.json"
        assert output_file.exists()

    def test_main_custom_output(self, temp_parsed_dir, sample_parsed_activity, monkeypatch):
        """Test main function with custom output file."""
        import sys
        from create_training_log import main

        # Create a parsed activity file
        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(sample_parsed_activity, f)

        custom_output = temp_parsed_dir / "custom_log.json"

        monkeypatch.setattr(sys, "argv", [
            "create_training_log.py",
            "--input-dir", str(temp_parsed_dir),
            "--output", str(custom_output)
        ])

        main()

        # Check custom output file was created
        assert custom_output.exists()

    def test_main_with_include_gps_flag(self, temp_parsed_dir, monkeypatch):
        """Test main function with --include-gps flag."""
        import sys
        from create_training_log import main

        # Note: The current implementation doesn't actually use this flag
        # but we test that it doesn't cause errors
        activity = {
            "date": "20251202",
            "metadata": {},
            "sources": {
                "csv": {"data": {"summary": {"getdistance": 2.0}}}
            }
        }

        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(activity, f)

        output_file = temp_parsed_dir / "training_log.json"

        monkeypatch.setattr(sys, "argv", [
            "create_training_log.py",
            "--input-dir", str(temp_parsed_dir),
            "--output", str(output_file),
            "--include-gps"
        ])

        main()

        assert output_file.exists()
