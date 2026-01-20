#!/usr/bin/env python3
"""
Coros Running Data Parser
Parses FIT, TCX, and CSV files from Coros running watch exports
and creates comprehensive JSON files for AI training analysis.
"""

import os
import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import re


class CorosDataParser:
    """Parser for Coros running data in multiple formats."""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)

    def parse_csv_splits(self, csv_path: Path) -> Dict[str, Any]:
        """Parse CSV file containing split data."""
        splits = []
        summary = {}

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Clean up whitespace from values
                row = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}

                if row.get('Split') == 'Summary':
                    summary = self._clean_split_row(row)
                else:
                    splits.append(self._clean_split_row(row))

        return {
            'splits': splits,
            'summary': summary
        }

    def _clean_split_row(self, row: Dict) -> Dict[str, Any]:
        """Clean and convert split row data to appropriate types."""
        cleaned = {}
        for key, value in row.items():
            if not value or value == '':
                continue

            # Convert numeric values
            if key in ['GetDistance', 'Elevation Gain', 'Elev Loss']:
                try:
                    cleaned[key.lower().replace(' ', '_')] = float(value)
                except ValueError:
                    cleaned[key.lower().replace(' ', '_')] = value
            elif key in ['Avg Run Cadence', 'Max Run Cadence', 'Avg Stride Length',
                        'Avg HR', 'Max HR', 'Avg Temperature', 'Calories']:
                try:
                    cleaned[key.lower().replace(' ', '_')] = int(value)
                except ValueError:
                    cleaned[key.lower().replace(' ', '_')] = value
            else:
                cleaned[key.lower().replace(' ', '_')] = value

        return cleaned

    def parse_tcx(self, tcx_path: Path) -> Dict[str, Any]:
        """Parse TCX file containing detailed GPS and sensor data."""
        tree = ET.parse(tcx_path)
        root = tree.getroot()

        # Define namespace
        ns = {
            'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
            'ext': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'
        }

        activity_data = {
            'activity_type': None,
            'activity_id': None,
            'laps': [],
            'trackpoints': []
        }

        # Get activity info
        activity = root.find('.//tcx:Activity', ns)
        if activity is not None:
            activity_data['activity_type'] = activity.get('Sport')
            activity_id = activity.find('tcx:Id', ns)
            if activity_id is not None:
                activity_data['activity_id'] = activity_id.text

        # Parse laps
        for lap in root.findall('.//tcx:Lap', ns):
            lap_data = {
                'start_time': lap.get('StartTime'),
                'total_time_seconds': self._get_float(lap, 'tcx:TotalTimeSeconds', ns),
                'distance_meters': self._get_float(lap, 'tcx:DistanceMeters', ns),
                'max_speed': self._get_float(lap, 'tcx:MaximumSpeed', ns),
                'calories': self._get_int(lap, 'tcx:Calories', ns),
                'avg_hr': self._get_int(lap, 'tcx:AverageHeartRateBpm/tcx:Value', ns),
                'max_hr': self._get_int(lap, 'tcx:MaximumHeartRateBpm/tcx:Value', ns),
                'intensity': self._get_text(lap, 'tcx:Intensity', ns),
                'trigger_method': self._get_text(lap, 'tcx:TriggerMethod', ns)
            }

            # Clean None values
            lap_data = {k: v for k, v in lap_data.items() if v is not None}
            activity_data['laps'].append(lap_data)

        # Parse trackpoints (detailed GPS and sensor data)
        trackpoint_count = 0
        max_trackpoints = 10000  # Limit to avoid extremely large JSON files

        for trackpoint in root.findall('.//tcx:Trackpoint', ns):
            if trackpoint_count >= max_trackpoints:
                break

            tp_data = {
                'time': self._get_text(trackpoint, 'tcx:Time', ns),
            }

            # Position (GPS)
            position = trackpoint.find('tcx:Position', ns)
            if position is not None:
                lat = self._get_float(position, 'tcx:LatitudeDegrees', ns)
                lon = self._get_float(position, 'tcx:LongitudeDegrees', ns)
                if lat is not None and lon is not None:
                    tp_data['position'] = {'lat': lat, 'lon': lon}

            # Other metrics
            altitude = self._get_float(trackpoint, 'tcx:AltitudeMeters', ns)
            distance = self._get_float(trackpoint, 'tcx:DistanceMeters', ns)
            hr = self._get_int(trackpoint, 'tcx:HeartRateBpm/tcx:Value', ns)

            # Extensions (speed, cadence, etc.)
            extensions = trackpoint.find('tcx:Extensions', ns)
            if extensions is not None:
                # Speed might be a direct child
                speed_elem = extensions.find('Speed')
                if speed_elem is not None:
                    try:
                        tp_data['speed_ms'] = float(speed_elem.text)
                    except (ValueError, TypeError):
                        pass

            if altitude is not None:
                tp_data['altitude_m'] = altitude
            if distance is not None:
                tp_data['distance_m'] = distance
            if hr is not None:
                tp_data['heart_rate'] = hr

            # Only add trackpoint if it has useful data
            if len(tp_data) > 1:  # More than just time
                activity_data['trackpoints'].append(tp_data)
                trackpoint_count += 1

        return activity_data

    def _get_text(self, element, path: str, ns: dict) -> Optional[str]:
        """Safely get text from XML element."""
        found = element.find(path, ns)
        return found.text if found is not None else None

    def _get_float(self, element, path: str, ns: dict) -> Optional[float]:
        """Safely get float from XML element."""
        text = self._get_text(element, path, ns)
        if text is not None:
            try:
                return float(text)
            except ValueError:
                return None
        return None

    def _get_int(self, element, path: str, ns: dict) -> Optional[int]:
        """Safely get int from XML element."""
        text = self._get_text(element, path, ns)
        if text is not None:
            try:
                return int(float(text))
            except ValueError:
                return None
        return None

    def parse_fit(self, fit_path: Path) -> Dict[str, Any]:
        """Parse FIT file (requires fitparse library)."""
        try:
            from fitparse import FitFile

            fitfile = FitFile(str(fit_path))
            fit_data = {
                'records': [],
                'laps': [],
                'session': {}
            }

            for record in fitfile.get_messages():
                msg_type = record.name

                if msg_type == 'record':
                    # GPS and sensor records
                    record_data = {}
                    for field in record:
                        if field.value is not None:
                            record_data[field.name] = field.value
                    if record_data:
                        fit_data['records'].append(record_data)

                elif msg_type == 'lap':
                    lap_data = {}
                    for field in record:
                        if field.value is not None:
                            lap_data[field.name] = field.value
                    if lap_data:
                        fit_data['laps'].append(lap_data)

                elif msg_type == 'session':
                    for field in record:
                        if field.value is not None:
                            fit_data['session'][field.name] = field.value

            return fit_data

        except ImportError:
            return {
                'error': 'fitparse library not installed',
                'install_command': 'pip install fitparse'
            }
        except Exception as e:
            return {
                'error': f'Failed to parse FIT file: {str(e)}'
            }

    def parse_activity(self, date_folder: Path, verbose: bool = True) -> Dict[str, Any]:
        """Parse all data files for a single activity."""
        activity_data = {
            'date': date_folder.name,
            'parsed_at': datetime.now().isoformat(),
            'metadata': {},
            'sources': {}
        }

        # Read metadata.json if it exists
        metadata_file = date_folder / 'metadata.json'
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    activity_data['metadata'] = json.load(f)
                if verbose:
                    run_type = activity_data['metadata'].get('run_type', 'unknown')
                    print(f"  Run type: {run_type}")
            except Exception as e:
                activity_data['metadata'] = {'error': f'Failed to read metadata: {str(e)}'}

        # Find all files in the folder
        files = list(date_folder.glob('*'))

        csv_files = [f for f in files if f.suffix == '.csv']
        tcx_files = [f for f in files if f.suffix == '.tcx']
        fit_files = [f for f in files if f.suffix == '.fit']

        # Report files found
        if verbose:
            print(f"  Found files: ", end='')
            file_types = []
            if csv_files:
                file_types.append(f"CSV ({csv_files[0].name})")
            if tcx_files:
                file_types.append(f"TCX ({tcx_files[0].name})")
            if fit_files:
                file_types.append(f"FIT ({fit_files[0].name})")
            print(', '.join(file_types) if file_types else 'None')

        # Parse CSV (splits and summary)
        if csv_files:
            try:
                if verbose:
                    print(f"  Parsing CSV...")
                csv_data = self.parse_csv_splits(csv_files[0])
                activity_data['sources']['csv'] = {
                    'file': csv_files[0].name,
                    'data': csv_data
                }
            except Exception as e:
                activity_data['sources']['csv'] = {
                    'error': str(e)
                }

        # Parse TCX (detailed trackpoints)
        if tcx_files:
            try:
                if verbose:
                    print(f"  Parsing TCX...")
                tcx_data = self.parse_tcx(tcx_files[0])
                activity_data['sources']['tcx'] = {
                    'file': tcx_files[0].name,
                    'data': tcx_data
                }
            except Exception as e:
                activity_data['sources']['tcx'] = {
                    'error': str(e)
                }

        # Parse FIT (most complete data)
        if fit_files:
            try:
                if verbose:
                    print(f"  Parsing FIT...")
                fit_data = self.parse_fit(fit_files[0])
                activity_data['sources']['fit'] = {
                    'file': fit_files[0].name,
                    'data': fit_data
                }
            except Exception as e:
                activity_data['sources']['fit'] = {
                    'error': str(e)
                }

        return activity_data

    def process_all_activities(self, output_dir: str = "./parsed_data") -> None:
        """Process all activities in the data directory."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Find all date folders
        date_folders = [d for d in self.data_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        date_folders.sort()

        print(f"Found {len(date_folders)} activities to process")

        for date_folder in date_folders:
            print(f"\nProcessing {date_folder.name}...")

            try:
                activity_data = self.parse_activity(date_folder)

                # Save to JSON
                output_file = output_path / f"{date_folder.name}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(activity_data, f, indent=2, ensure_ascii=False, default=str)

                print(f"  ✓ Saved to {output_file}")

                # Print summary
                if 'csv' in activity_data['sources'] and 'data' in activity_data['sources']['csv']:
                    csv_data = activity_data['sources']['csv']['data']
                    if 'summary' in csv_data:
                        summary = csv_data['summary']
                        print(f"  Distance: {summary.get('getdistance', 'N/A')} km")
                        print(f"  Time: {summary.get('time', 'N/A')}")
                        print(f"  Avg Pace: {summary.get('avg_pace', 'N/A')}")
                        print(f"  Avg HR: {summary.get('avg_hr', 'N/A')} bpm")

            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
                import traceback
                traceback.print_exc()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Parse Coros running data to JSON')
    parser.add_argument('--data-dir', default='./data',
                      help='Directory containing YYYYMMDD folders with activity data')
    parser.add_argument('--output-dir', default='./parsed_data',
                      help='Directory to save parsed JSON files')
    parser.add_argument('--single-date',
                      help='Process only a specific date (YYYYMMDD format)')

    args = parser.parse_args()

    parser_obj = CorosDataParser(args.data_dir)

    if args.single_date:
        date_folder = Path(args.data_dir) / args.single_date
        if not date_folder.exists():
            print(f"Error: Folder {date_folder} does not exist")
            return

        print(f"Processing {args.single_date}...")
        activity_data = parser_obj.parse_activity(date_folder)

        output_path = Path(args.output_dir)
        output_path.mkdir(exist_ok=True)
        output_file = output_path / f"{args.single_date}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(activity_data, f, indent=2, ensure_ascii=False, default=str)

        print(f"✓ Saved to {output_file}")
    else:
        parser_obj.process_all_activities(args.output_dir)

    print("\n✓ Processing complete!")

    # Check if fitparse is installed
    try:
        import fitparse
        print("\n✓ FIT file parsing enabled (fitparse installed)")
    except ImportError:
        print("\n⚠ To parse FIT files (most complete data), install: pip install fitparse")


if __name__ == '__main__':
    main()
