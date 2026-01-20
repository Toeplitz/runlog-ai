"""
Tests for create_training_log.py module.
"""

import pytest
import json
from pathlib import Path
from create_training_log import (
    aggregate_training_data,
    create_chunks,
    calculate_chunk_statistics,
    create_index_file
)


class TestAggregateTrainingData:
    """Tests for aggregate_training_data function."""

    def test_aggregate_with_single_activity(self, temp_parsed_dir, sample_parsed_activity):
        """Test aggregating a single activity."""
        # Create a parsed activity file
        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(sample_parsed_activity, f)

        output_file = temp_parsed_dir / "training_log.json"
        # Use chunk_size=0 to disable chunking for single file test
        aggregate_training_data(str(temp_parsed_dir), str(output_file), chunk_size=0)

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
        aggregate_training_data(str(temp_parsed_dir), str(output_file), chunk_size=0)

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
        aggregate_training_data(str(temp_parsed_dir), str(output_file), chunk_size=0)

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
        aggregate_training_data(str(temp_parsed_dir), str(output_file), chunk_size=0)

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
        aggregate_training_data(str(temp_parsed_dir), str(output_file), chunk_size=0)

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
        aggregate_training_data(str(temp_parsed_dir), str(output_file), chunk_size=0)

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
        aggregate_training_data(str(temp_parsed_dir), str(output_file), chunk_size=0)

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
        aggregate_training_data(str(temp_parsed_dir), str(output_file), chunk_size=0)

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
        aggregate_training_data(str(temp_parsed_dir), str(output_file), chunk_size=0)

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


class TestChunkingFunctions:
    """Tests for chunking functionality."""

    def test_create_chunks_basic(self):
        """Test basic chunk creation."""
        activities = [{"id": i} for i in range(25)]
        chunks = create_chunks(activities, 10)

        assert len(chunks) == 3
        assert len(chunks[0]) == 10
        assert len(chunks[1]) == 10
        assert len(chunks[2]) == 5

    def test_create_chunks_exact_multiple(self):
        """Test chunking when activities are exact multiple of chunk size."""
        activities = [{"id": i} for i in range(20)]
        chunks = create_chunks(activities, 10)

        assert len(chunks) == 2
        assert len(chunks[0]) == 10
        assert len(chunks[1]) == 10

    def test_create_chunks_smaller_than_chunk_size(self):
        """Test chunking when fewer activities than chunk size."""
        activities = [{"id": i} for i in range(5)]
        chunks = create_chunks(activities, 10)

        assert len(chunks) == 1
        assert len(chunks[0]) == 5

    def test_create_chunks_size_one(self):
        """Test chunking with chunk_size=1."""
        activities = [{"id": i} for i in range(3)]
        chunks = create_chunks(activities, 1)

        assert len(chunks) == 3
        assert all(len(chunk) == 1 for chunk in chunks)

    def test_create_chunks_zero_or_negative(self):
        """Test chunking with chunk_size <= 0 returns single chunk."""
        activities = [{"id": i} for i in range(10)]

        chunks_zero = create_chunks(activities, 0)
        assert len(chunks_zero) == 1
        assert len(chunks_zero[0]) == 10

        chunks_negative = create_chunks(activities, -5)
        assert len(chunks_negative) == 1
        assert len(chunks_negative[0]) == 10

    def test_calculate_chunk_statistics(self):
        """Test statistics calculation for a chunk."""
        activities = [
            {
                "summary": {
                    "getdistance": 5.0,
                    "time": "00:35:00",
                    "calories": 300
                }
            },
            {
                "summary": {
                    "getdistance": 3.0,
                    "time": "00:21:00",
                    "calories": 180
                }
            }
        ]

        stats = calculate_chunk_statistics(activities)

        assert stats["total_distance_km"] == 8.0
        assert stats["total_time_formatted"] == "00:56:00"
        assert stats["total_calories"] == 480
        assert stats["average_distance_per_run"] == 4.0

    def test_calculate_chunk_statistics_with_invalid_data(self):
        """Test statistics with invalid numeric values."""
        activities = [
            {
                "summary": {
                    "getdistance": "invalid",
                    "time": "invalid:time",
                    "calories": "N/A"
                }
            },
            {
                "summary": {
                    "getdistance": 5.0,
                    "time": "00:30:00",
                    "calories": 250
                }
            }
        ]

        stats = calculate_chunk_statistics(activities)

        # Should handle invalid data gracefully
        assert stats["total_distance_km"] == 5.0
        assert stats["total_time_formatted"] == "00:30:00"
        assert stats["total_calories"] == 250

    def test_calculate_chunk_statistics_without_summary(self):
        """Test statistics with activities missing summary."""
        activities = [
            {"date": "20251201"},
            {
                "summary": {
                    "getdistance": 2.0,
                    "time": "00:14:00",
                    "calories": 120
                }
            }
        ]

        stats = calculate_chunk_statistics(activities)

        assert stats["total_distance_km"] == 2.0
        assert stats["total_calories"] == 120

    def test_create_index_file(self, temp_parsed_dir):
        """Test index file creation."""
        chunks_info = [
            {
                "file": "training_log_part1.json",
                "chunk_number": 1,
                "activity_count": 10,
                "date_range": {
                    "first_activity": "20251201",
                    "last_activity": "20251210"
                },
                "statistics": {
                    "total_distance_km": 50.0,
                    "total_calories": 3000
                }
            },
            {
                "file": "training_log_part2.json",
                "chunk_number": 2,
                "activity_count": 5,
                "date_range": {
                    "first_activity": "20251211",
                    "last_activity": "20251215"
                },
                "statistics": {
                    "total_distance_km": 25.0,
                    "total_calories": 1500
                }
            }
        ]

        index_file = temp_parsed_dir / "training_log_index.json"
        create_index_file(chunks_info, str(index_file))

        assert index_file.exists()

        with open(index_file, 'r') as f:
            index_data = json.load(f)

        assert "metadata" in index_data
        assert index_data["metadata"]["total_chunks"] == 2
        assert index_data["metadata"]["total_activities"] == 15
        assert "chunks" in index_data
        assert len(index_data["chunks"]) == 2

    def test_aggregate_with_chunking(self, temp_parsed_dir):
        """Test aggregating with chunking enabled."""
        # Create 25 activities
        for i in range(1, 26):
            activity = {
                "date": f"202512{i:02d}" if i <= 31 else f"202601{i-31:02d}",
                "metadata": {"run_type": "outdoor"},
                "sources": {
                    "csv": {
                        "data": {
                            "summary": {
                                "getdistance": 5.0,
                                "time": "00:35:00",
                                "calories": 300
                            }
                        }
                    }
                }
            }
            activity_file = temp_parsed_dir / f"activity_{i:02d}.json"
            with open(activity_file, 'w') as f:
                json.dump(activity, f)

        # Aggregate with chunk_size=10
        output_file = temp_parsed_dir / "training_log.json"
        chunks_dir = temp_parsed_dir / "chunks"
        aggregate_training_data(
            str(temp_parsed_dir),
            str(output_file),
            chunk_size=10,
            chunks_dir=str(chunks_dir)
        )

        # Check that chunk files were created in chunks directory
        chunk1 = chunks_dir / "training_log_part1.json"
        chunk2 = chunks_dir / "training_log_part2.json"
        chunk3 = chunks_dir / "training_log_part3.json"
        index_file = chunks_dir / "training_log_index.json"

        assert chunk1.exists()
        assert chunk2.exists()
        assert chunk3.exists()
        assert index_file.exists()

        # Verify chunk contents
        with open(chunk1, 'r') as f:
            chunk1_data = json.load(f)
        assert chunk1_data["metadata"]["total_activities"] == 10
        assert chunk1_data["metadata"]["chunk_number"] == 1
        assert len(chunk1_data["activities"]) == 10

        with open(chunk3, 'r') as f:
            chunk3_data = json.load(f)
        assert chunk3_data["metadata"]["total_activities"] == 5
        assert chunk3_data["metadata"]["chunk_number"] == 3
        assert len(chunk3_data["activities"]) == 5

        # Verify index file
        with open(index_file, 'r') as f:
            index_data = json.load(f)
        assert index_data["metadata"]["total_chunks"] == 3
        assert index_data["metadata"]["total_activities"] == 25

        # Temp directory cleanup is automatic, no manual cleanup needed

    def test_aggregate_with_custom_chunk_pattern(self, temp_parsed_dir):
        """Test chunking with custom file pattern."""
        # Create 15 activities
        for i in range(1, 16):
            activity = {
                "date": f"202512{i:02d}",
                "metadata": {},
                "sources": {
                    "csv": {
                        "data": {
                            "summary": {
                                "getdistance": 3.0,
                                "time": "00:21:00",
                                "calories": 180
                            }
                        }
                    }
                }
            }
            activity_file = temp_parsed_dir / f"activity_{i:02d}.json"
            with open(activity_file, 'w') as f:
                json.dump(activity, f)

        # Aggregate with custom chunk pattern
        output_file = temp_parsed_dir / "training_log.json"
        chunks_dir = temp_parsed_dir / "custom_chunks"
        aggregate_training_data(
            str(temp_parsed_dir),
            str(output_file),
            chunk_size=5,
            chunk_pattern="runs_{}_of_3.json",
            chunks_dir=str(chunks_dir)
        )

        # Check custom named files in chunks directory
        chunk1 = chunks_dir / "runs_1_of_3.json"
        chunk2 = chunks_dir / "runs_2_of_3.json"
        chunk3 = chunks_dir / "runs_3_of_3.json"

        assert chunk1.exists()
        assert chunk2.exists()
        assert chunk3.exists()

        # Temp directory cleanup is automatic, no manual cleanup needed

    def test_aggregate_no_chunking_when_below_threshold(self, temp_parsed_dir):
        """Test that chunking is not used when activities <= chunk_size."""
        # Create only 5 activities
        for i in range(1, 6):
            activity = {
                "date": f"202512{i:02d}",
                "metadata": {},
                "sources": {
                    "csv": {
                        "data": {
                            "summary": {
                                "getdistance": 5.0,
                                "time": "00:35:00",
                                "calories": 300
                            }
                        }
                    }
                }
            }
            activity_file = temp_parsed_dir / f"activity_{i:02d}.json"
            with open(activity_file, 'w') as f:
                json.dump(activity, f)

        # Try to chunk with chunk_size=10 (more than total activities)
        output_file = temp_parsed_dir / "training_log.json"
        chunks_dir = temp_parsed_dir / "chunks"
        aggregate_training_data(
            str(temp_parsed_dir),
            str(output_file),
            chunk_size=10,
            chunks_dir=str(chunks_dir)
        )

        # Should create single file, not chunks
        assert output_file.exists()
        # Chunks directory should not be created when not chunking
        assert not chunks_dir.exists()

        with open(output_file, 'r') as f:
            data = json.load(f)
        assert data["metadata"]["total_activities"] == 5
        assert len(data["activities"]) == 5

    def test_aggregate_backward_compatibility_no_chunking(self, temp_parsed_dir, sample_parsed_activity):
        """Test that no chunking occurs with chunk_size=0."""
        # Create a parsed activity file
        activity_file = temp_parsed_dir / "20251202.json"
        with open(activity_file, 'w') as f:
            json.dump(sample_parsed_activity, f)

        # Call with chunk_size=0 to disable chunking
        output_file = temp_parsed_dir / "training_log.json"
        chunks_dir = temp_parsed_dir / "chunks"
        aggregate_training_data(str(temp_parsed_dir), str(output_file), chunk_size=0, chunks_dir=str(chunks_dir))

        # Should create single file, no chunks directory
        assert output_file.exists()
        assert not chunks_dir.exists()

        with open(output_file, 'r') as f:
            training_log = json.load(f)

        assert training_log["metadata"]["total_activities"] == 1
        assert "chunk_number" not in training_log["metadata"]
