"""
Tests for parse_coros_data.py module.
"""

import pytest
import json
from pathlib import Path
from parse_coros_data import CorosDataParser


class TestCorosDataParser:
    """Tests for CorosDataParser class."""

    def test_init_default_data_dir(self):
        """Test initialization with default data directory."""
        parser = CorosDataParser()
        assert parser.data_dir == Path("./data")

    def test_init_custom_data_dir(self, temp_data_dir):
        """Test initialization with custom data directory."""
        parser = CorosDataParser(str(temp_data_dir))
        assert parser.data_dir == temp_data_dir

    def test_parse_csv_splits(self, temp_data_dir, sample_csv_content):
        """Test parsing CSV file with splits data."""
        # Create CSV file
        csv_file = temp_data_dir / "test.csv"
        csv_file.write_text(sample_csv_content)

        parser = CorosDataParser(str(temp_data_dir))
        result = parser.parse_csv_splits(csv_file)

        # Verify structure
        assert "splits" in result
        assert "summary" in result
        assert len(result["splits"]) == 2

        # Verify first split
        split1 = result["splits"][0]
        assert split1["split"] == "1"
        assert split1["getdistance"] == 1.0
        assert split1["time"] == "00:07:10"
        assert split1["avg_hr"] == 135

        # Verify summary
        summary = result["summary"]
        assert summary["split"] == "Summary"
        assert summary["getdistance"] == 2.0
        assert summary["avg_hr"] == 136
        assert summary["calories"] == 172

    def test_parse_csv_splits_with_empty_values(self, temp_data_dir):
        """Test parsing CSV with empty values."""
        csv_content = """Split,GetDistance,Time,Avg HR
1,1.00,00:07:10,
Summary,2.00,00:14:15,136"""

        csv_file = temp_data_dir / "test.csv"
        csv_file.write_text(csv_content)

        parser = CorosDataParser(str(temp_data_dir))
        result = parser.parse_csv_splits(csv_file)

        # Empty values should not be included
        assert "avg_hr" not in result["splits"][0]
        assert result["summary"]["avg_hr"] == 136

    def test_clean_split_row_numeric_conversions(self):
        """Test _clean_split_row converts numeric values correctly."""
        parser = CorosDataParser()

        row = {
            "GetDistance": "1.5",
            "Avg HR": "145",
            "Avg Run Cadence": "170",
            "Time": "00:07:10",
            "": ""
        }

        cleaned = parser._clean_split_row(row)

        assert cleaned["getdistance"] == 1.5
        assert cleaned["avg_hr"] == 145
        assert cleaned["avg_run_cadence"] == 170
        assert cleaned["time"] == "00:07:10"
        assert "" not in cleaned

    def test_clean_split_row_invalid_numeric(self):
        """Test _clean_split_row handles invalid numeric values."""
        parser = CorosDataParser()

        row = {
            "GetDistance": "N/A",
            "Avg HR": "invalid"
        }

        cleaned = parser._clean_split_row(row)

        # Should keep as string if conversion fails
        assert cleaned["getdistance"] == "N/A"
        assert cleaned["avg_hr"] == "invalid"

    def test_parse_tcx(self, temp_data_dir, sample_tcx_content):
        """Test parsing TCX file."""
        tcx_file = temp_data_dir / "activity.tcx"
        tcx_file.write_text(sample_tcx_content)

        parser = CorosDataParser(str(temp_data_dir))
        result = parser.parse_tcx(tcx_file)

        # Verify structure
        assert result["activity_type"] == "Running"
        assert result["activity_id"] == "2025-12-02T12:42:40Z"
        assert len(result["laps"]) == 1
        assert len(result["trackpoints"]) == 2

        # Verify lap data
        lap = result["laps"][0]
        assert lap["start_time"] == "2025-12-02T12:42:40Z"
        assert lap["total_time_seconds"] == 856.0
        assert lap["distance_meters"] == 2000.0
        assert lap["avg_hr"] == 136
        assert lap["max_hr"] == 148

        # Verify trackpoint data
        tp1 = result["trackpoints"][0]
        assert tp1["time"] == "2025-12-02T12:42:40Z"
        assert tp1["position"]["lat"] == 58.881234
        assert tp1["position"]["lon"] == 5.663456
        assert tp1["altitude_m"] == 10.0
        assert tp1["heart_rate"] == 85

        tp2 = result["trackpoints"][1]
        assert tp2["time"] == "2025-12-02T12:42:41Z"
        assert tp2["position"]["lat"] == 58.881244
        assert tp2["position"]["lon"] == 5.663466
        # Note: Speed element parsing not currently supported

    def test_parse_tcx_without_position(self, temp_data_dir):
        """Test parsing TCX trackpoint without GPS position."""
        tcx_content = """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2">
  <Activities>
    <Activity Sport="Running">
      <Id>2025-12-02T12:42:40Z</Id>
      <Lap StartTime="2025-12-02T12:42:40Z">
        <Track>
          <Trackpoint>
            <Time>2025-12-02T12:42:40Z</Time>
            <HeartRateBpm>
              <Value>85</Value>
            </HeartRateBpm>
          </Trackpoint>
        </Track>
      </Lap>
    </Activity>
  </Activities>
</TrainingCenterDatabase>"""

        tcx_file = temp_data_dir / "activity.tcx"
        tcx_file.write_text(tcx_content)

        parser = CorosDataParser(str(temp_data_dir))
        result = parser.parse_tcx(tcx_file)

        # Should still have trackpoint without position
        assert len(result["trackpoints"]) == 1
        assert "position" not in result["trackpoints"][0]
        assert result["trackpoints"][0]["heart_rate"] == 85

    def test_get_text_helper_methods(self, temp_data_dir, sample_tcx_content):
        """Test helper methods for extracting XML data."""
        import xml.etree.ElementTree as ET

        tcx_file = temp_data_dir / "activity.tcx"
        tcx_file.write_text(sample_tcx_content)

        parser = CorosDataParser(str(temp_data_dir))
        tree = ET.parse(tcx_file)
        root = tree.getroot()

        ns = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
        activity = root.find('.//tcx:Activity', ns)

        # Test _get_text
        activity_id = parser._get_text(activity, 'tcx:Id', ns)
        assert activity_id == "2025-12-02T12:42:40Z"

        # Test _get_float
        lap = root.find('.//tcx:Lap', ns)
        time_seconds = parser._get_float(lap, 'tcx:TotalTimeSeconds', ns)
        assert time_seconds == 856.0

        # Test _get_int
        hr = parser._get_int(lap, 'tcx:AverageHeartRateBpm/tcx:Value', ns)
        assert hr == 136

    def test_get_methods_with_none(self):
        """Test helper methods return None for missing elements."""
        import xml.etree.ElementTree as ET

        parser = CorosDataParser()
        element = ET.fromstring("<root></root>")
        ns = {}

        assert parser._get_text(element, "missing", ns) is None
        assert parser._get_float(element, "missing", ns) is None
        assert parser._get_int(element, "missing", ns) is None

    def test_get_float_with_invalid_value(self):
        """Test _get_float with invalid numeric value."""
        import xml.etree.ElementTree as ET

        parser = CorosDataParser()
        element = ET.fromstring("<root><value>invalid</value></root>")
        ns = {}

        assert parser._get_float(element, "value", ns) is None

    def test_parse_fit_without_fitparse(self, temp_data_dir, monkeypatch):
        """Test parse_fit when fitparse is not installed."""
        # Mock ImportError for fitparse
        import builtins
        import sys

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "fitparse":
                raise ImportError("No module named 'fitparse'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        parser = CorosDataParser(str(temp_data_dir))
        fit_file = temp_data_dir / "activity.fit"
        fit_file.write_bytes(b"dummy fit data")

        result = parser.parse_fit(fit_file)

        assert "error" in result
        assert "fitparse library not installed" in result["error"]

    def test_parse_activity(self, sample_activity_folder):
        """Test parsing a complete activity folder."""
        parser = CorosDataParser(str(sample_activity_folder.parent))
        result = parser.parse_activity(sample_activity_folder, verbose=False)

        # Verify basic structure
        assert result["date"] == "20251202"
        assert "parsed_at" in result
        assert "metadata" in result
        assert "sources" in result

        # Verify metadata
        assert result["metadata"]["run_type"] == "outdoor"
        assert result["metadata"]["title"] == "Test Morning Run"

        # Verify CSV data parsed
        assert "csv" in result["sources"]
        assert "data" in result["sources"]["csv"]
        assert "splits" in result["sources"]["csv"]["data"]

        # Verify TCX data parsed
        assert "tcx" in result["sources"]
        assert "data" in result["sources"]["tcx"]
        assert result["sources"]["tcx"]["data"]["activity_type"] == "Running"

    def test_parse_activity_without_metadata(self, temp_data_dir, sample_csv_content):
        """Test parsing activity without metadata file."""
        activity_dir = temp_data_dir / "20251202"
        activity_dir.mkdir()

        csv_file = activity_dir / "activity.csv"
        csv_file.write_text(sample_csv_content)

        parser = CorosDataParser(str(temp_data_dir))
        result = parser.parse_activity(activity_dir, verbose=False)

        # Should have empty metadata
        assert result["metadata"] == {}

    def test_parse_activity_with_invalid_metadata(self, temp_data_dir, sample_csv_content):
        """Test parsing activity with invalid metadata JSON."""
        activity_dir = temp_data_dir / "20251202"
        activity_dir.mkdir()

        csv_file = activity_dir / "activity.csv"
        csv_file.write_text(sample_csv_content)

        metadata_file = activity_dir / "metadata.json"
        metadata_file.write_text("invalid json")

        parser = CorosDataParser(str(temp_data_dir))
        result = parser.parse_activity(activity_dir, verbose=False)

        # Should have error in metadata
        assert "error" in result["metadata"]

    def test_parse_activity_csv_error(self, temp_data_dir):
        """Test parsing activity when CSV parsing fails."""
        activity_dir = temp_data_dir / "20251202"
        activity_dir.mkdir()

        # Create invalid CSV
        csv_file = activity_dir / "activity.csv"
        csv_file.write_text("invalid csv format")

        parser = CorosDataParser(str(temp_data_dir))
        result = parser.parse_activity(activity_dir, verbose=False)

        # CSV source should exist but might have no splits/summary
        # or an error depending on how csv.DictReader handles it
        assert "csv" in result["sources"]

    def test_process_all_activities(self, temp_data_dir, temp_parsed_dir, sample_activity_folder):
        """Test processing all activities in a directory."""
        # Create another activity
        activity_dir2 = temp_data_dir / "20251204"
        activity_dir2.mkdir()

        csv_content = """Split,GetDistance,Time,Avg HR
Summary,3.00,00:21:00,140"""
        csv_file = activity_dir2 / "activity.csv"
        csv_file.write_text(csv_content)

        parser = CorosDataParser(str(temp_data_dir))
        parser.process_all_activities(str(temp_parsed_dir))

        # Check output files were created
        output_files = list(temp_parsed_dir.glob("*.json"))
        assert len(output_files) == 2

        # Verify one of the files
        json_file = temp_parsed_dir / "20251202.json"
        assert json_file.exists()

        with open(json_file, 'r') as f:
            data = json.load(f)

        assert data["date"] == "20251202"

    def test_process_all_activities_empty_dir(self, temp_data_dir, temp_parsed_dir, capsys):
        """Test processing with no activity folders."""
        parser = CorosDataParser(str(temp_data_dir))
        parser.process_all_activities(str(temp_parsed_dir))

        captured = capsys.readouterr()
        assert "Found 0 activities" in captured.out

    def test_process_all_activities_with_error(self, temp_data_dir, temp_parsed_dir, monkeypatch):
        """Test processing activities when one fails."""
        # Create two activities
        activity_dir1 = temp_data_dir / "20251202"
        activity_dir1.mkdir()

        activity_dir2 = temp_data_dir / "20251204"
        activity_dir2.mkdir()

        # Mock parse_activity to fail for the second one
        original_parse = CorosDataParser.parse_activity
        call_count = [0]

        def mock_parse(self, date_folder, verbose=True):
            call_count[0] += 1
            if call_count[0] == 2:
                raise Exception("Test error")
            return original_parse(self, date_folder, verbose)

        monkeypatch.setattr(CorosDataParser, "parse_activity", mock_parse)

        parser = CorosDataParser(str(temp_data_dir))
        parser.process_all_activities(str(temp_parsed_dir))

        # Should continue processing despite error
        # First one should have been saved
        json_file = temp_parsed_dir / "20251202.json"
        assert json_file.exists()


class TestMainFunction:
    """Tests for the main function and CLI."""

    def test_main_with_single_date(self, temp_data_dir, temp_parsed_dir, sample_activity_folder, monkeypatch):
        """Test main function with --single-date argument."""
        import sys
        from parse_coros_data import main

        monkeypatch.setattr(sys, "argv", [
            "parse_coros_data.py",
            "--data-dir", str(temp_data_dir),
            "--output-dir", str(temp_parsed_dir),
            "--single-date", "20251202"
        ])

        main()

        # Check output file was created
        output_file = temp_parsed_dir / "20251202.json"
        assert output_file.exists()

    def test_main_with_nonexistent_date(self, temp_data_dir, temp_parsed_dir, monkeypatch, capsys):
        """Test main function with non-existent date."""
        import sys
        from parse_coros_data import main

        monkeypatch.setattr(sys, "argv", [
            "parse_coros_data.py",
            "--data-dir", str(temp_data_dir),
            "--output-dir", str(temp_parsed_dir),
            "--single-date", "20991231"
        ])

        main()

        captured = capsys.readouterr()
        assert "does not exist" in captured.out

    def test_main_process_all(self, temp_data_dir, temp_parsed_dir, sample_activity_folder, monkeypatch):
        """Test main function processing all activities."""
        import sys
        from parse_coros_data import main

        monkeypatch.setattr(sys, "argv", [
            "parse_coros_data.py",
            "--data-dir", str(temp_data_dir),
            "--output-dir", str(temp_parsed_dir)
        ])

        main()

        # Check output files were created
        output_files = list(temp_parsed_dir.glob("*.json"))
        assert len(output_files) >= 1
