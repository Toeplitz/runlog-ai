#!/usr/bin/env python3
"""
View and summarize parsed training data from Coros exports.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def parse_time_to_seconds(time_str):
    """Convert HH:MM:SS format to total seconds."""
    if not time_str or time_str == 'N/A':
        return 0
    try:
        parts = time_str.strip().split(':')
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + int(s)
        elif len(parts) == 2:
            m, s = parts
            return int(m) * 60 + int(s)
    except:
        return 0


def format_pace(pace_str):
    """Format pace string nicely."""
    if not pace_str:
        return "N/A"
    return pace_str.strip()


def summarize_activity(json_file):
    """Print a summary of a single activity."""
    with open(json_file, 'r') as f:
        data = json.load(f)

    print(f"\n{'='*80}")
    print(f"Date: {data['date']}")

    # Show title if present
    if 'metadata' in data and data['metadata']:
        metadata = data['metadata']
        if metadata.get('title'):
            print(f"Title: {metadata['title']}")

    print(f"{'='*80}")

    # Metadata
    if 'metadata' in data and data['metadata']:
        metadata = data['metadata']
        if 'error' not in metadata:
            print("\nMETADATA")
            print("-" * 80)
            print(f"  Run Type:        {metadata.get('run_type', 'N/A')}")
            if metadata.get('title'):
                print(f"  Title:           {metadata.get('title')}")
            if metadata.get('notes'):
                print(f"  Notes:           {metadata.get('notes')}")

    # CSV Summary Data
    if 'csv' in data['sources'] and 'data' in data['sources']['csv']:
        csv_data = data['sources']['csv']['data']
        if 'summary' in csv_data:
            summary = csv_data['summary']
            print("\nSUMMARY")
            print("-" * 80)
            print(f"  Distance:        {summary.get('getdistance', 'N/A')} km")
            print(f"  Time:            {summary.get('time', 'N/A')}")
            print(f"  Moving Time:     {summary.get('moving_time', 'N/A')}")
            print(f"  Avg Pace:        {format_pace(summary.get('avg_pace', 'N/A'))} /km")
            print(f"  Best Pace:       {format_pace(summary.get('best_pace', 'N/A'))} /km")
            print(f"  Avg HR:          {summary.get('avg_hr', 'N/A')} bpm")
            print(f"  Max HR:          {summary.get('max_hr', 'N/A')} bpm")
            print(f"  Avg Cadence:     {summary.get('avg_run_cadence', 'N/A')} spm")
            print(f"  Avg Stride:      {summary.get('avg_stride_length', 'N/A')} cm")
            print(f"  Elevation Gain:  {summary.get('elevation_gain', 'N/A')} m")
            print(f"  Elevation Loss:  {summary.get('elev_loss', 'N/A')} m")
            print(f"  Avg Temperature: {summary.get('avg_temperature', 'N/A')} °C")
            print(f"  Calories:        {summary.get('calories', 'N/A')} kcal")

        # Split Data
        if 'splits' in csv_data:
            splits = csv_data['splits']
            print(f"\nSPLITS ({len(splits)} total)")
            print("-" * 80)
            print(f"{'#':<4} {'Dist(km)':<10} {'Time':<12} {'Pace':<12} {'HR':<8} {'Cad':<8} {'Elev+':<8}")
            print("-" * 80)

            for split in splits:
                split_num = split.get('split', '?')
                dist = split.get('getdistance', 0)
                time = split.get('time', 'N/A')
                pace = format_pace(split.get('avg_pace', 'N/A'))
                hr = split.get('avg_hr', 'N/A')
                cad = split.get('avg_run_cadence', 'N/A')
                elev = split.get('elevation_gain', 0)

                print(f"{split_num:<4} {dist:<10.2f} {time:<12} {pace:<12} {hr:<8} {cad:<8} {elev:<8}")

    # TCX Data Info
    if 'tcx' in data['sources'] and 'data' in data['sources']['tcx']:
        tcx_data = data['sources']['tcx']['data']
        print(f"\nTCX DATA")
        print("-" * 80)
        print(f"  Activity Type:   {tcx_data.get('activity_type', 'N/A')}")
        print(f"  Activity ID:     {tcx_data.get('activity_id', 'N/A')}")
        print(f"  Laps:            {len(tcx_data.get('laps', []))}")
        print(f"  Trackpoints:     {len(tcx_data.get('trackpoints', []))} GPS points")

        # Show first and last GPS coordinates
        trackpoints = tcx_data.get('trackpoints', [])
        if trackpoints:
            first = trackpoints[0]
            last = trackpoints[-1]
            if 'position' in first:
                print(f"  Start Position:  {first['position']['lat']:.6f}, {first['position']['lon']:.6f}")
            if 'position' in last:
                print(f"  End Position:    {last['position']['lat']:.6f}, {last['position']['lon']:.6f}")

    # FIT Data Info
    if 'fit' in data['sources'] and 'data' in data['sources']['fit']:
        fit_data = data['sources']['fit']['data']
        if 'error' not in fit_data:
            print(f"\nFIT DATA")
            print("-" * 80)
            print(f"  Records:         {len(fit_data.get('records', []))}")
            print(f"  Laps:            {len(fit_data.get('laps', []))}")
            print(f"  Session Data:    {len(fit_data.get('session', {}))} fields")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='View parsed Coros training data')
    parser.add_argument('--dir', default='./parsed_data',
                      help='Directory containing parsed JSON files')
    parser.add_argument('--date',
                      help='View specific date (YYYYMMDD format)')
    parser.add_argument('--list', action='store_true',
                      help='List all available activities')

    args = parser.parse_args()

    data_dir = Path(args.dir)

    if not data_dir.exists():
        print(f"Error: Directory {data_dir} does not exist")
        print("Run parse_coros_data.py first to generate parsed data")
        return

    json_files = sorted(data_dir.glob('*.json'))

    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return

    if args.list:
        print(f"\nFound {len(json_files)} activities:")
        print("-" * 80)
        for jf in json_files:
            with open(jf, 'r') as f:
                data = json.load(f)
            summary = data.get('sources', {}).get('csv', {}).get('data', {}).get('summary', {})
            dist = summary.get('getdistance', 'N/A')
            time = summary.get('time', 'N/A')
            pace = format_pace(summary.get('avg_pace', 'N/A'))
            print(f"  {jf.stem}  -  {dist} km  |  {time}  |  {pace}/km")
        return

    if args.date:
        json_file = data_dir / f"{args.date}.json"
        if not json_file.exists():
            print(f"Error: {json_file} does not exist")
            return
        summarize_activity(json_file)
    else:
        # Show all activities
        for json_file in json_files:
            summarize_activity(json_file)


if __name__ == '__main__':
    main()
