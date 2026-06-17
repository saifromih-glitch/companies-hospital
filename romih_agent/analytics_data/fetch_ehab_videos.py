#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import subprocess, json, os

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

print("=" * 60)
print("Fetching Dr. Ehab Moslem's YouTube videos...")
print("=" * 60)

# Get channel videos
result = subprocess.run([
    'yt-dlp', '--flat-playlist', '--print', '%(id)s|%(title)s|%(duration)s|%(view_count)s',
    'https://www.youtube.com/@ehabmes/videos', '--playlist-end', '500'
], capture_output=True, text=True, encoding='utf-8')

# Save raw output
raw_path = os.path.join(WORK_DIR, 'ehab_videos_raw.txt')
with open(raw_path, 'w', encoding='utf-8') as f:
    f.write(result.stdout)

lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
print(f'Total videos found: {len(lines)}')

# Filter for long-form content (>20 min = >1200 seconds, >10 min = >600)
long_videos = []
medium_videos = []
shorts = []
for line in lines:
    parts = line.strip().split('|')
    if len(parts) >= 3:
        vid_id = parts[0]
        title = parts[1]
        dur_str = parts[2]
        try:
            dur = float(dur_str) if dur_str else 0
        except:
            dur = 0
        entry = {'id': vid_id, 'title': title, 'duration': dur, 'views': parts[3] if len(parts) > 3 else 'NA'}
        if dur >= 1200:
            long_videos.append(entry)
        elif dur >= 600:
            medium_videos.append(entry)
        else:
            shorts.append(entry)

print(f'Long-form videos (>20min): {len(long_videos)}')
print(f'Medium videos (10-20min): {len(medium_videos)}')
print(f'Shorts (<10min): {len(shorts)}')

print('\n--- LONG VIDEOS (>20min) ---')
for v in long_videos:
    mins = int(v['duration'] // 60)
    print(f"  https://youtube.com/watch?v={v['id']} | {mins}min | {v['title']}")

print('\n--- MEDIUM VIDEOS (10-20min) ---')
for v in medium_videos[:30]:
    mins = int(v['duration'] // 60)
    print(f"  https://youtube.com/watch?v={v['id']} | {mins}min | {v['title']}")

# Also try to get "عيادة الشركات" playlist
print('\n--- Playlist: عيادة الشركات ---')
for playlist_url in [
    'https://www.youtube.com/playlist?list=PLGL8uBnUC-C-5PyvuXr8oP3fTPDXxDCyl'
]:
    result2 = subprocess.run([
        'yt-dlp', '--flat-playlist', '--print', '%(id)s|%(title)s|%(duration)s',
        playlist_url, '--playlist-end', '200'
    ], capture_output=True, text=True, encoding='utf-8')
    pl_lines = [l for l in result2.stdout.strip().split('\n') if l.strip()]
    print(f'  {len(pl_lines)} videos in playlist')
    for l in pl_lines[:30]:
        print(f'    {l}')

# Save structured video list
video_list = {
    'long_form': long_videos,
    'medium': medium_videos,
    'shorts_count': len(shorts),
    'total': len(lines)
}
json_path = os.path.join(WORK_DIR, 'ehab_video_list.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(video_list, f, ensure_ascii=False, indent=2)
print(f'\nVideo list saved to: {json_path}')
print(f'Long-form: {len(long_videos)} videos')
