# TRP Bot - YouTube Highlights via yt-dlp
# Uses yt-dlp to search and get video info

import subprocess
import json
import re
from datetime import datetime

def search_youtube(query, max_results=10):
    """
    Search YouTube using yt-dlp
    """
    try:
        cmd = [
            "yt-dlp",
            f"--playlist-end={max_results}",
            "--flat-playlist",
            f"--dump-json",
            f"ytsearch{max_results}:{query}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        videos = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    v = json.loads(line)
                    videos.append({
                        "video_id": v.get("id"),
                        "title": v.get("title"),
                        "duration": v.get("duration_string"),
                        "url": f"https://youtube.com/watch?v={v.get('id')}",
                        "thumbnail": v.get("thumbnail"),
                        "channel": v.get("uploader"),
                        "views": v.get("view_count"),
                        "upload_date": v.get("upload_date")
                    })
                except json.JSONDecodeError:
                    pass
        
        return {
            "source": "YouTube (yt-dlp)",
            "query": query,
            "videos": videos
        }
    
    except Exception as e:
        return {"error": str(e)}

def get_epl_highlights(max_results=10):
    """Get latest EPL highlights"""
    queries = [
        "Premier League highlights 2026",
        "EPL match highlights this week",
        "Premier League goals today"
    ]
    
    all_videos = []
    seen_ids = set()
    
    for query in queries:
        result = search_youtube(query, max_results)
        if "videos" in result:
            for video in result["videos"]:
                if video["video_id"] not in seen_ids:
                    seen_ids.add(video["video_id"])
                    video["query"] = query
                    all_videos.append(video)
        
        if len(all_videos) >= max_results * 2:
            break
    
    return {
        "source": "YouTube",
        "videos": all_videos[:max_results]
    }

def get_team_highlights(team_name, max_results=5):
    """Get highlights for a specific team"""
    queries = [
        f"{team_name} highlights Premier League 2026",
        f"{team_name} goals this week"
    ]
    
    all_videos = []
    seen_ids = set()
    
    for query in queries:
        result = search_youtube(query, max_results)
        if "videos" in result:
            for video in result["videos"]:
                if video["video_id"] not in seen_ids:
                    seen_ids.add(video["video_id"])
                    video["query"] = query
                    all_videos.append(video)
        
        if len(all_videos) >= max_results:
            break
    
    return {
        "source": "YouTube",
        "team": team_name,
        "videos": all_videos[:max_results]
    }

def get_official_channel_videos(channel_name, max_results=5):
    """Get latest videos from official PL channels"""
    
    # Channel search URLs
    channels = {
        "Premier League": "PL",
        "Sky Sports Football": "Sky Sports",
        "The Overlap": "The Overlap",
        "Football Daily": "Football Daily"
    }
    
    query = f"{channel_name} Premier League"
    result = search_youtube(query, max_results)
    
    return result

if __name__ == "__main__":
    print("=" * 50)
    print("Testing YouTube via yt-dlp")
    print("=" * 50)
    
    print("\n📺 Getting EPL highlights...")
    result = get_epl_highlights(max_results=10)
    
    if "videos" in result:
        print(f"Found {len(result['videos'])} videos:\n")
        for v in result["videos"]:
            print(f"  🎬 {v['title'][:50]}...")
            print(f"     {v['url']}")
            print(f"     ⏱️ {v['duration']} | 👁️ {v.get('views', 'N/A')} views")
            print()
    else:
        print(result)
