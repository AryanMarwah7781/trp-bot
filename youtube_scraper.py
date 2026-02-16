# TRP Bot - YouTube Highlights Scraper
# Fetches EPL match highlights from YouTube

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
}

def search_youtube_highlights(query, max_results=10):
    """
    Search YouTube for highlights using scraping (no API key needed)
    """
    # YouTube search URL
    url = f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        
        videos = []
        
        # Find video IDs in the page
        for script in soup.find_all("script"):
            script_text = script.string or ""
            if "ytInitialData" in script_text:
                # Extract JSON data
                match = re.search(r'ytInitialData\s*=\s*({.*?});', script_text, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        
                        # Navigate to video results
                        contents = data.get("contents", {})
                        two_col = contents.get("twoColumnSearchResultsRenderer", {})
                        results = two_col.get("primaryContents", {}).get("sectionListRenderer", {}).get("contents", [])
                        
                        for section in results:
                            items = section.get("itemSectionRenderer", {}).get("contents", [])
                            for item in items:
                                video = item.get("videoRenderer")
                                if video:
                                    video_id = video.get("videoId")
                                    title = video.get("title", {}).get("runs", [{}])[0].get("text", "")
                                    views = video.get("viewCountText", {}).get("simpleText", "")
                                    duration = video.get("lengthText", {}).get("simpleText", "")
                                    channel = video.get("ownerText", {}).get("runs", [{}])[0].get("text", "")
                                    
                                    if video_id and title:
                                        videos.append({
                                            "video_id": video_id,
                                            "title": title,
                                            "url": f"https://youtube.com/watch?v={video_id}",
                                            "views": views,
                                            "duration": duration,
                                            "channel": channel
                                        })
                                    
                                    if len(videos) >= max_results:
                                        break
                            if len(videos) >= max_results:
                                break
                    except json.JSONDecodeError:
                        pass
                break
        
        return {
            "source": "YouTube (scraped)",
            "query": query,
            "videos": videos
        }
    
    except Exception as e:
        return {"error": str(e)}

def get_epl_highlights_for_week(week_start_date):
    """
    Get highlights for a specific week
    week_start_date: datetime object for the start of the week
    """
    week_end = week_start_date + timedelta(days=7)
    
    queries = [
        f"EPL match highlights {week_start_date.strftime('%B %Y')}",
        f"Premier League week highlights {week_start_date.strftime('%Y-%m-%d')}",
        f"Premier League goals {week_start_date.strftime('%B %Y')}",
        f"Arsenal Liverpool Manchester United Chelsea Manchester City highlights"
    ]
    
    all_videos = []
    seen_ids = set()
    
    for query in queries:
        result = search_youtube_highlights(query, max_results=10)
        if "videos" in result:
            for video in result["videos"]:
                if video["video_id"] not in seen_ids:
                    seen_ids.add(video["video_id"])
                    video["query"] = query
                    all_videos.append(video)
        
        if len(all_videos) >= 20:
            break
    
    return {
        "week_start": week_start_date.isoformat(),
        "week_end": week_end.isoformat(),
        "videos": all_videos[:20]
    }

def get_team_highlights(team_name, max_results=5):
    """Get recent highlights for a specific team"""
    queries = [
        f"{team_name} highlights this week",
        f"{team_name} goals today",
        f"{team_name} match highlights Premier League"
    ]
    
    all_videos = []
    seen_ids = set()
    
    for query in queries:
        result = search_youtube_highlights(query, max_results=max_results)
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
        "videos": all_videos
    }

def get_top_channels():
    """Get videos from top football YouTube channels"""
    channels = [
        "Premier League",
        "Sky Sports Football",
        "BT Sport",
        "BBC Sport",
        "ESPN FC",
        "Football Daily",
        "The Overlap"
    ]
    
    all_videos = []
    
    for channel in channels:
        query = f"{channel} Premier League"
        result = search_youtube_highlights(query, max_results=5)
        if "videos" in result:
            for video in result["videos"]:
                video["channel_search"] = channel
                all_videos.append(video)
    
    return {
        "source": "YouTube",
        "channels": channels,
        "videos": all_videos
    }

if __name__ == "__main__":
    print("Testing YouTube scraper...")
    
    print("\n📺 Searching for EPL highlights...")
    result = search_youtube_highlights("Premier League highlights February 2026", max_results=5)
    
    if "videos" in result:
        print(f"Found {len(result['videos'])} videos:")
        for v in result["videos"]:
            print(f"  - {v['title'][:60]}...")
            print(f"    {v['url']}")
    else:
        print(result)
