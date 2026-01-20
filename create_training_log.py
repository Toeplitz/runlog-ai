#!/usr/bin/env python3
"""
Create a consolidated training log for AI analysis.
Aggregates all parsed activities into a single comprehensive JSON file.
Supports chunking large training logs into manageable pieces.
"""

import json
from pathlib import Path
from datetime import datetime


def create_chunks(activities: list, chunk_size: int) -> list:
    """
    Split activities into chunks of specified size.

    Args:
        activities: List of activity dictionaries
        chunk_size: Number of activities per chunk

    Returns:
        List of activity chunks (each chunk is a list of activities)
    """
    if chunk_size <= 0:
        return [activities]

    return [activities[i:i+chunk_size]
            for i in range(0, len(activities), chunk_size)]


def calculate_chunk_statistics(activities: list) -> dict:
    """
    Calculate statistics for a chunk of activities.

    Args:
        activities: List of activity dictionaries

    Returns:
        Dictionary with chunk statistics
    """
    total_distance = 0
    total_time_seconds = 0
    total_calories = 0

    for activity in activities:
        # Extract CSV summary data if available
        if 'summary' in activity:
            summary = activity['summary']
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

    return {
        'total_distance_km': round(total_distance, 2),
        'total_time_formatted': f"{total_time_seconds // 3600:02d}:{(total_time_seconds % 3600) // 60:02d}:{total_time_seconds % 60:02d}",
        'total_calories': total_calories,
        'average_distance_per_run': round(total_distance / len(activities), 2) if activities else 0
    }


def create_index_file(chunks_info: list, output_file: str):
    """
    Create an index file describing all chunks.

    Args:
        chunks_info: List of dictionaries with chunk information
        output_file: Path to index file
    """
    index = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "total_chunks": len(chunks_info),
            "total_activities": sum(c['activity_count'] for c in chunks_info),
            "purpose": "Index file for chunked training log"
        },
        "chunks": chunks_info
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"✓ Index file created: {output_file}")


def aggregate_training_data(
    parsed_dir: str = "./parsed_data",
    output_file: str = "training_log.json",
    chunk_size: int = 5,
    chunk_pattern: str = "training_log_part{}.json",
    chunks_dir: str = "training_log_chunks"
):
    """
    Aggregate all parsed activities into a training log optimized for AI analysis.

    Args:
        parsed_dir: Directory containing parsed JSON files
        output_file: Output file name (used as base for chunks if chunking)
        chunk_size: Number of activities per chunk (0 = no chunking, default: 5)
        chunk_pattern: File pattern for chunks (e.g., "training_log_part{}.json")
        chunks_dir: Directory to store chunk files (default: "training_log_chunks")
    """
    data_dir = Path(parsed_dir)

    if not data_dir.exists():
        print(f"Error: Directory {data_dir} does not exist")
        return

    json_files = sorted(data_dir.glob('*.json'))

    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return

    # Aggregate all activities first
    activities = []
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

        activities.append(activity_summary)

    # Calculate overall statistics
    overall_statistics = {
        'total_distance_km': round(total_distance, 2),
        'total_time_formatted': f"{total_time_seconds // 3600:02d}:{(total_time_seconds % 3600) // 60:02d}:{total_time_seconds % 60:02d}",
        'total_calories': total_calories,
        'average_distance_per_run': round(total_distance / len(json_files), 2) if json_files else 0,
        'date_range': {
            'first_activity': json_files[0].stem if json_files else None,
            'last_activity': json_files[-1].stem if json_files else None
        }
    }

    # Check if chunking is requested
    if chunk_size > 0 and len(activities) > chunk_size:
        # Create chunks
        chunks = create_chunks(activities, chunk_size)
        chunks_info = []

        # Create chunks directory
        chunks_path = Path(chunks_dir)
        chunks_path.mkdir(parents=True, exist_ok=True)

        print(f"\nCreating {len(chunks)} chunks with ~{chunk_size} activities each...")
        print(f"Storing chunks in: {chunks_path.absolute()}")

        for idx, chunk in enumerate(chunks, start=1):
            # Create chunk training log
            chunk_log = {
                "metadata": {
                    "athlete_name": "Training Log",
                    "created_at": datetime.now().isoformat(),
                    "chunk_number": idx,
                    "total_chunks": len(chunks),
                    "total_activities": len(chunk),
                    "data_source": "Coros Running Watch",
                    "purpose": "AI Training Coach Analysis (Chunk)"
                },
                "activities": chunk
            }

            # Calculate chunk statistics
            chunk_stats = calculate_chunk_statistics(chunk)
            chunk_log['metadata']['statistics'] = chunk_stats

            # Determine chunk file name
            chunk_filename = chunk_pattern.format(idx)
            chunk_file_path = chunks_path / chunk_filename

            # Save chunk file
            with open(chunk_file_path, 'w', encoding='utf-8') as f:
                json.dump(chunk_log, f, indent=2, ensure_ascii=False, default=str)

            print(f"  ✓ Chunk {idx}/{len(chunks)}: {chunk_filename} ({len(chunk)} activities)")

            # Track chunk info for index
            chunks_info.append({
                "file": chunk_filename,  # Use just the filename, not full path
                "chunk_number": idx,
                "activity_count": len(chunk),
                "date_range": {
                    "first_activity": chunk[0]['date'] if chunk else None,
                    "last_activity": chunk[-1]['date'] if chunk else None
                },
                "statistics": chunk_stats
            })

        # Create index file in chunks directory
        index_filename = 'training_log_index.json'
        index_file = chunks_path / index_filename
        create_index_file(chunks_info, str(index_file))

        print(f"\n✓ Created {len(chunks)} chunk files")
        print(f"\nOVERALL STATISTICS:")
        print(f"  Total Activities: {len(json_files)}")
        print(f"  Total Distance:   {overall_statistics['total_distance_km']} km")
        print(f"  Total Time:       {overall_statistics['total_time_formatted']}")
        print(f"  Total Calories:   {total_calories} kcal")
        print(f"  Avg Distance:     {overall_statistics['average_distance_per_run']} km/run")
        print(f"\nChunk files are ready to be provided to an AI training coach for analysis!")

    else:
        # No chunking - create single file as before
        training_log = {
            "metadata": {
                "athlete_name": "Training Log",
                "created_at": datetime.now().isoformat(),
                "total_activities": len(json_files),
                "data_source": "Coros Running Watch",
                "purpose": "AI Training Coach Analysis"
            },
            "activities": activities
        }

        training_log['metadata']['statistics'] = overall_statistics

        # Save consolidated training log
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_log, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n✓ Training log created: {output_path}")
        print(f"\nSTATISTICS:")
        print(f"  Total Activities: {len(json_files)}")
        print(f"  Total Distance:   {overall_statistics['total_distance_km']} km")
        print(f"  Total Time:       {overall_statistics['total_time_formatted']}")
        print(f"  Total Calories:   {total_calories} kcal")
        print(f"  Avg Distance:     {overall_statistics['average_distance_per_run']} km/run")
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
    parser.add_argument('--chunk-size', type=int, default=5,
                      help='Number of activities per chunk (0 = no chunking, default: 5)')
    parser.add_argument('--chunk-output-pattern', default='training_log_part{}.json',
                      help='File pattern for chunks (default: training_log_part{}.json)')
    parser.add_argument('--chunks-dir', default='training_log_chunks',
                      help='Directory to store chunk files (default: training_log_chunks)')

    args = parser.parse_args()

    aggregate_training_data(
        args.input_dir,
        args.output,
        args.chunk_size,
        args.chunk_output_pattern,
        args.chunks_dir
    )


if __name__ == '__main__':
    main()
