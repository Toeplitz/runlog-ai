#!/usr/bin/env python3
"""
Create a consolidated training log for AI analysis.
Aggregates all parsed activities into a single comprehensive JSON file.
"""

import json
from pathlib import Path
from datetime import datetime


def aggregate_training_data(parsed_dir: str = "./parsed_data", output_file: str = "training_log.json"):
    """
    Aggregate all parsed activities into a single training log optimized for AI analysis.
    """
    data_dir = Path(parsed_dir)

    if not data_dir.exists():
        print(f"Error: Directory {data_dir} does not exist")
        return

    json_files = sorted(data_dir.glob('*.json'))

    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return

    training_log = {
        "metadata": {
            "athlete_name": "Training Log",
            "created_at": datetime.now().isoformat(),
            "total_activities": len(json_files),
            "data_source": "Coros Running Watch",
            "purpose": "AI Training Coach Analysis"
        },
        "activities": []
    }

    total_distance = 0
    total_time_seconds = 0
    total_calories = 0

    print(f"Aggregating {len(json_files)} activities...")

    for json_file in json_files:
        with open(json_file, 'r') as f:
            activity_data = json.load(f)

        # Extract key information for AI analysis
        activity_summary = {
            "date": activity_data['date'],
            "metadata": activity_data.get('metadata', {}),
            "raw_data_files": activity_data['sources']
        }

        # Add CSV summary if available
        if 'csv' in activity_data['sources'] and 'data' in activity_data['sources']['csv']:
            csv_data = activity_data['sources']['csv']['data']

            if 'summary' in csv_data:
                summary = csv_data['summary']
                activity_summary['summary'] = summary

                # Track totals
                try:
                    total_distance += float(summary.get('getdistance', 0))
                except:
                    pass
                try:
                    total_calories += int(summary.get('calories', 0))
                except:
                    pass
                try:
                    time_str = summary.get('time', '00:00:00')
                    parts = time_str.strip().split(':')
                    if len(parts) == 3:
                        h, m, s = map(int, parts)
                        total_time_seconds += h * 3600 + m * 60 + s
                except:
                    pass

            if 'splits' in csv_data:
                activity_summary['splits'] = csv_data['splits']

        # Add TCX metadata
        if 'tcx' in activity_data['sources'] and 'data' in activity_data['sources']['tcx']:
            tcx_data = activity_data['sources']['tcx']['data']
            activity_summary['tcx_metadata'] = {
                'activity_type': tcx_data.get('activity_type'),
                'activity_id': tcx_data.get('activity_id'),
                'total_trackpoints': len(tcx_data.get('trackpoints', [])),
                'total_laps': len(tcx_data.get('laps', []))
            }

            # Optionally include GPS track for route analysis
            # Note: Commenting this out to keep file size manageable
            # Uncomment if you want full GPS data in the training log
            # activity_summary['gps_track'] = tcx_data.get('trackpoints', [])

        training_log['activities'].append(activity_summary)

    # Add aggregated statistics
    training_log['metadata']['statistics'] = {
        'total_distance_km': round(total_distance, 2),
        'total_time_formatted': f"{total_time_seconds // 3600:02d}:{(total_time_seconds % 3600) // 60:02d}:{total_time_seconds % 60:02d}",
        'total_calories': total_calories,
        'average_distance_per_run': round(total_distance / len(json_files), 2) if json_files else 0,
        'date_range': {
            'first_activity': json_files[0].stem if json_files else None,
            'last_activity': json_files[-1].stem if json_files else None
        }
    }

    # Save consolidated training log
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(training_log, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n✓ Training log created: {output_path}")
    print(f"\nSTATISTICS:")
    print(f"  Total Activities: {len(json_files)}")
    print(f"  Total Distance:   {training_log['metadata']['statistics']['total_distance_km']} km")
    print(f"  Total Time:       {training_log['metadata']['statistics']['total_time_formatted']}")
    print(f"  Total Calories:   {total_calories} kcal")
    print(f"  Avg Distance:     {training_log['metadata']['statistics']['average_distance_per_run']} km/run")
    print(f"\nThis file is ready to be provided to an AI training coach for analysis!")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Create consolidated training log for AI analysis'
    )
    parser.add_argument('--input-dir', default='./parsed_data',
                      help='Directory containing parsed JSON files')
    parser.add_argument('--output', default='training_log.json',
                      help='Output file name for training log')
    parser.add_argument('--include-gps', action='store_true',
                      help='Include full GPS trackpoints (creates larger file)')

    args = parser.parse_args()

    aggregate_training_data(args.input_dir, args.output)


if __name__ == '__main__':
    main()
