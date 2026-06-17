#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, json, subprocess, os

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(WORK_DIR, 'podcast_metadata.txt')

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=" * 60 + "\n")
    f.write("Dr. Ehab Moslem - Podcast Appearances\n")
    f.write("=" * 60 + "\n\n")
    
    vids_to_check = ['DsL8aiF7HGg', 'cAXtd0Q6ysA', 'aCXYfFEXJ6M']
    
    for vid in vids_to_check:
        result = subprocess.run([
            'yt-dlp', f'https://youtube.com/watch?v={vid}',
            '--dump-json', '--skip-download'
        ], capture_output=True)
        data = json.loads(result.stdout)
        title = data.get('title', 'Unknown')
        channel = data.get('channel', 'Unknown')
        duration = data.get('duration', 0)
        desc = data.get('description', '')[:500]
        upload_date = data.get('upload_date', '?')
        f.write(f'=== {vid} ===\n')
        f.write(f'URL: https://youtube.com/watch?v={vid}\n')
        f.write(f'Title: {title}\n')
        f.write(f'Channel: {channel}\n')
        f.write(f'Duration: {duration}s ({duration//60}min)\n')
        f.write(f'Date: {upload_date}\n')
        f.write(f'Desc snippet: {desc}\n')
        f.write('\n')

    # Get playlist longer videos
    f.write('=== Playlist: عيادة الشركات - Long videos ===\n')
    result = subprocess.run([
        'yt-dlp', 'https://www.youtube.com/playlist?list=PLGL8uBnUC-C-5PyvuXr8oP3fTPDXxDCyl',
        '--dump-json', '--skip-download', '--playlist-end', '101'
    ], capture_output=True)
    if result.stdout and result.stdout.strip():
        text_output = result.stdout.decode('utf-8') if isinstance(result.stdout, bytes) else result.stdout
        for line in text_output.strip().split('\n'):
            try:
                data = json.loads(line)
                duration = data.get('duration', 0)
                if duration and duration >= 600:
                    f.write(f"  {data['id']} | {duration//60}min | {data['title']}\n")
            except:
                pass

    # Also get the main channel long videos
    f.write('\n=== Main Channel (@ehabmes) - Videos >10min ===\n')
    result = subprocess.run([
        'yt-dlp', 'https://www.youtube.com/@ehabmes/videos',
        '--dump-json', '--skip-download', '--playlist-end', '500'
    ], capture_output=True)
    if result.stdout and result.stdout.strip():
        text_output = result.stdout.decode('utf-8') if isinstance(result.stdout, bytes) else result.stdout
        for line in text_output.strip().split('\n'):
            try:
                data = json.loads(line)
                duration = data.get('duration', 0)
                if duration and duration >= 600:
                    f.write(f"  {data['id']} | {duration//60}min | {data['title']} | views: {data.get('view_count', '?')}\n")
            except:
                pass

print(f"Metadata written to {output_file}")
print("Done!")
