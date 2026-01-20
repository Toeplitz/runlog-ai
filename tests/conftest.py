"""
Pytest configuration and shared fixtures for runlog-ai tests.
"""

import pytest
import json
import tempfile
from pathlib import Path


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def temp_parsed_dir(tmp_path):
    """Create a temporary parsed data directory for testing."""
    parsed_dir = tmp_path / "parsed_data"
    parsed_dir.mkdir()
    return parsed_dir


@pytest.fixture
def sample_csv_content():
    """Sample CSV content for testing."""
    return """Split,GetDistance,Time,Moving Time,Avg Pace,Best Pace,Avg Run Cadence,Max Run Cadence,Avg Stride Length,Avg HR,Max HR,Elevation Gain,Elev Loss,Avg Temperature,Calories
1,1.00,00:07:10,00:07:10,00:07:10,00:06:50,170,180,95,135,145,5,3,12,85
2,1.00,00:07:05,00:07:05,00:07:05,00:06:45,172,182,96,138,148,4,2,12,87
Summary,2.00,00:14:15,00:14:15,00:07:07,00:06:45,171,182,95,136,148,9,5,12,172"""


@pytest.fixture
def sample_tcx_content():
    """Sample TCX content for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2">
  <Activities>
    <Activity Sport="Running">
      <Id>2025-12-02T12:42:40Z</Id>
      <Lap StartTime="2025-12-02T12:42:40Z">
        <TotalTimeSeconds>856.0</TotalTimeSeconds>
        <DistanceMeters>2000.0</DistanceMeters>
        <MaximumSpeed>4.5</MaximumSpeed>
        <Calories>172</Calories>
        <AverageHeartRateBpm>
          <Value>136</Value>
        </AverageHeartRateBpm>
        <MaximumHeartRateBpm>
          <Value>148</Value>
        </MaximumHeartRateBpm>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
        <Track>
          <Trackpoint>
            <Time>2025-12-02T12:42:40Z</Time>
            <Position>
              <LatitudeDegrees>58.881234</LatitudeDegrees>
              <LongitudeDegrees>5.663456</LongitudeDegrees>
            </Position>
            <AltitudeMeters>10.0</AltitudeMeters>
            <DistanceMeters>0.0</DistanceMeters>
            <HeartRateBpm>
              <Value>85</Value>
            </HeartRateBpm>
            <Extensions>
              <Speed>0.0</Speed>
            </Extensions>
          </Trackpoint>
          <Trackpoint>
            <Time>2025-12-02T12:42:41Z</Time>
            <Position>
              <LatitudeDegrees>58.881244</LatitudeDegrees>
              <LongitudeDegrees>5.663466</LongitudeDegrees>
            </Position>
            <AltitudeMeters>11.0</AltitudeMeters>
            <DistanceMeters>5.0</DistanceMeters>
            <HeartRateBpm>
              <Value>90</Value>
            </HeartRateBpm>
            <Extensions>
              <Speed>4.93</Speed>
            </Extensions>
          </Trackpoint>
        </Track>
      </Lap>
    </Activity>
  </Activities>
</TrainingCenterDatabase>"""


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing."""
    return {
        "run_type": "outdoor",
        "title": "Test Morning Run",
        "notes": "Felt strong, good weather",
        "workout_type": "tempo",
        "perceived_effort": "8/10"
    }


@pytest.fixture
def sample_activity_folder(temp_data_dir, sample_csv_content, sample_tcx_content, sample_metadata):
    """Create a complete sample activity folder with all files."""
    activity_date = "20251202"
    activity_dir = temp_data_dir / activity_date
    activity_dir.mkdir()

    # Create CSV file
    csv_file = activity_dir / "activity.csv"
    csv_file.write_text(sample_csv_content)

    # Create TCX file
    tcx_file = activity_dir / "activity.tcx"
    tcx_file.write_text(sample_tcx_content)

    # Create metadata file
    metadata_file = activity_dir / "metadata.json"
    metadata_file.write_text(json.dumps(sample_metadata, indent=2))

    return activity_dir


@pytest.fixture
def sample_parsed_activity():
    """Sample parsed activity data for testing."""
    return {
        "date": "20251202",
        "parsed_at": "2025-12-02T10:00:00",
        "metadata": {
            "run_type": "outdoor",
            "title": "Test Morning Run",
            "workout_type": "tempo"
        },
        "sources": {
            "csv": {
                "file": "activity.csv",
                "data": {
                    "splits": [
                        {
                            "split": "1",
                            "getdistance": 1.0,
                            "time": "00:07:10",
                            "avg_pace": "00:07:10",
                            "avg_hr": 135
                        }
                    ],
                    "summary": {
                        "getdistance": 2.0,
                        "time": "00:14:15",
                        "avg_pace": "00:07:07",
                        "avg_hr": 136,
                        "calories": 172
                    }
                }
            },
            "tcx": {
                "file": "activity.tcx",
                "data": {
                    "activity_type": "Running",
                    "activity_id": "2025-12-02T12:42:40Z",
                    "laps": [
                        {
                            "start_time": "2025-12-02T12:42:40Z",
                            "total_time_seconds": 856.0,
                            "distance_meters": 2000.0
                        }
                    ],
                    "trackpoints": [
                        {
                            "time": "2025-12-02T12:42:40Z",
                            "position": {"lat": 58.881234, "lon": 5.663456},
                            "altitude_m": 10.0,
                            "heart_rate": 85
                        }
                    ]
                }
            }
        }
    }
