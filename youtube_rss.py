# TRP Bot - YouTube Highlights via RSS
# Uses YouTube RSS feeds for official channels

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import json

# Official PL channels RSS feeds
RSS_FEEDS = {
    "Premier League": "https://www.youtube.com/feeds/videos.xml?channel_id=UC-4L4KXt71X2gLhe-1I5Q0w",
    "Sky Sports": "https://www.youtube.com/feeds/videos.xml?channel_id=UCHP4GPMR2l3c2JqI2p7lE6g",
    "BBC Sport": "https://www.youtube.com/feeds/videos.xml?channel_id=UCwX6rVkOq0p4N2cE1W2p8rA",
    "ESPN FC": "https://www.youtube.com/feeds/videos.xml?channel_id=UCMtJMa7Xa4U3I3qZ3t7k9Qw",
    "Football Daily": "https://www.youtube.com/feeds/videos.xml?channel_id=UCwWdT_9hTjL9L4E2SGG-a0g",
    "The Overlap": "https://www.youtube.com/feeds/videos.xml?channel_id=UC_zKxT7e1L_tq3e5pX5j4Vw"
}

def get_rss_videos(channel_name, max_results=10):
    """Get videos from a YouTube channel RSS feed"""
    if channel_name not in RSS_FEEDS:
        return {"error": f"Unknown channel: {channel_name}"}
    
    try:
        url = RSS_FEEDS[channel_name]
        response = requests.get(url, timeout=15)
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # YouTube namespace
        ns = {'yt': 'http://www.youtube.com/xml/schemas/2015',
              'media': 'http://search.yahoo.com/mrss/'}
        
        videos = []
        for entry in root.findall('entry')[:max_results]:
            video_id = entry.find('yt:videoId', ns).text if entry.find('yt:videoId', ns) is not None else ""
            title = entry.find('title').text or ""
            published = entry.find('published').text if entry.find('published') is not None else ""
            thumbnail = ""
            media_group = entry.find('media:group', ns)
            if media_group:
                thumbnail = media_group.find('media:thumbnail', ns).get('url', "") if media_group.find('media:thumbnail', ns) is not None else ""
            
            videos.append({
                "video_id": video_id,
                "title": title,
                "published": published,
                "thumbnail": thumbnail,
                "url": f"https://youtube.com/watch?v={video_id}"
            })
        
        return {
            "channel": channel_name,
            "videos": videos
        }
    
    except Exception as e:
        return {"error": str(e), "channel": channel_name}

def get_all_highlights(max_per_channel=5):
    """Get highlights from all configured channels"""
    all_videos = []
    
    for channel in RSS_FEEDS.keys():
        result = get_rss_videos(channel, max_per_channel)
        if "videos" in result:
            for v in result["videos"]:
                v["source_channel"] = channel
                all_videos.append(v)
    
    # Sort by published date
    all_videos.sort(key=lambda x: x.get("published", ""), reverse=True)
    
    return {
        "sources": list(RSS_FEEDS.keys()),
        "total_videos": len(all_videos),
        "videos": all_videos
    }

def filter_epl_videos(videos):
    """Filter for EPL-related videos"""
    epl_keywords = [
        "premier league", "epl", "arsenal", "liverpool", "chelsea", 
        "manchester united", "man city", "tottenham", "newcastle",
        " Aston Villa", "west ham", "fulham", "crystal palace",
        "brentford", "nottingham forest", "bournemouth", "wolves",
        "everton", "southampton", "leicester", "ipswich"
    ]
    
    filtered = []
    for video in videos:
        title = video.get("title", "").lower()
        if any(kw in title for kw in epl_keywords):
            filtered.append(video)
    
    return filtered

if __name__ == "__main__":
    print("=" * 50)
    print("Testing YouTube RSS Feeds")
    print("=" * 50)
    
    print("\n📺 Getting highlights from all channels...")
    result = get_all_highlights(max_per_channel=5)
    
    print(f"Sources: {result['sources']}")
    print(f"Total videos: {result['total_videos']}")
    
    print("\n🎬 Latest videos:")
    for v in result["videos"][:10]:
        print(f"  - [{v['source_channel']}] {v['title'][:50]}...")
        print(f"    {v['url']}")
    
    # Filter for EPL
    epl = filter_epl_videos(result["videos"])
    print(f"\n⚽ EPL-specific videos: {len(epl)}")
