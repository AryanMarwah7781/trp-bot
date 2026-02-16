# TRP Bot - Extended Data Sources
# More data sources for the AI podcast

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
}

# ============================================
# BBC SPORT - Match Commentary
# ============================================
def get_bbc_live_scores():
    """Get live Premier League scores from BBC"""
    url = "https://www.bbc.com/sport/football/premier-league/scores"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        matches = []
        # BBC structure changes often, basic parsing
        for match in soup.find_all("article", {"class": "ssrcss-1que3b3-Promo"}):
            try:
                title = match.find("h3")
                if title:
                    matches.append(title.text.strip())
            except:
                pass
        
        return {"source": "BBC", "matches": matches[:10]}
    except Exception as e:
        return {"error": str(e)}

# ============================================
# SKY SPORTS - Latest News
# ============================================
def get_sky_sports_news():
    """Get latest EPL news from Sky Sports"""
    url = "https://www.skysports.com/football/news"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        articles = []
        for article in soup.find_all("a", {"class": "news-list__link"})[:15]:
            title = article.get("title") or article.text.strip()
            if title and len(title) > 10:
                articles.append({
                    "title": title[:100],
                    "url": "https://skysports.com" + article.get("href", "")
                })
        
        return {"source": "Sky Sports", "articles": articles}
    except Exception as e:
        return {"error": str(e)}

# ============================================
# YOUTUBE - Match Highlights & Comments
# ============================================
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

def search_youtube_videos(query, max_results=10):
    """Search YouTube for videos"""
    if not YOUTUBE_API_KEY:
        return {"error": "No YouTube API key"}
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        videos = []
        for item in data.get("items", []):
            videos.append({
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "videoId": item["id"]["videoId"],
                "published": item["snippet"]["publishedAt"]
            })
        
        return {"source": "YouTube", "videos": videos}
    except Exception as e:
        return {"error": str(e)}

# ============================================
# TRANSFERMARKT - Transfer News
# ============================================
def get_transfermarkt_rumours():
    """Get latest transfer rumours"""
    url = "https://www.transfermarkt.com/transfers/transfers/gerate_id/bs1/saison_id/2024"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Basic - would need proper parsing
        return {
            "source": "Transfermarkt",
            "note": "Would need API access for full data",
            "url": url
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================
# WHOscored - Match Stats
# ============================================
def get_whoscored_matches():
    """Get WhoScored match data"""
    url = "https://www.whoscored.com/Matches/1958489/Live/England-Premier-League-2024-2025-Arsenal-Crystal-Palace"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        return {
            "source": "WhoScored",
            "status": "Page loaded, parsing would require Selenium",
            "url": url
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================
# ESPN API - Live Scores
# ============================================
def get_espn_scores(date=None):
    """Get scores from ESPN API"""
    import datetime
    if date is None:
        date = datetime.datetime.now()
    
    date_str = date.strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates={date_str}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        matches = []
        for event in data.get("events", []):
            comp = event.get("competitions", [{}])[0]
            match = {
                "id": event.get("id"),
                "name": event.get("name"),
                "status": event.get("status", {}).get("detail"),
            }
            
            for side in ["home", "away"]:
                if side in comp:
                    team = comp[side].get("team", {})
                    match[f"{side}_team"] = team.get("displayName")
                    match[f"{side}_score"] = comp[side].get("score", {}).get("displayValue")
            
            matches.append(match)
        
        return {"source": "ESPN", "date": date_str, "matches": matches}
    except Exception as e:
        return {"error": str(e)}

# ============================================
# TWITTER/X - Hashtag Trends (No API)
# ============================================
def get_twitter_trends():
    """Try to get trending from Twitter (limited without API)"""
    # Note: Twitter API is now paid ($100/mo minimum)
    # This is just a placeholder
    return {
        "source": "Twitter",
        "status": "API is paid now ($100+/month)",
        "alternative": "Use Reddit for social buzz instead"
    }

# ============================================
# FLASHSCORE - Live Data
# ============================================
def get_flashscore_live():
    """Get live scores from Flashscore"""
    url = "https://www.flashscore.com/football/england/premier-league/"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        return {
            "source": "Flashscore",
            "status": "Page loaded, JS-rendered content needs Selenium",
            "url": url
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================
# TEST ALL SOURCES
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("Testing Data Sources")
    print("=" * 50)
    
    print("\n📰 BBC Live Scores...")
    print(json.dumps(get_bbc_live_scores(), indent=2)[:500])
    
    print("\n📰 Sky Sports News...")
    result = get_sky_sports_news()
    if "articles" in result:
        print(f"Got {len(result['articles'])} articles")
        for a in result["articles"][:3]:
            print(f"  - {a['title'][:60]}...")
    else:
        print(result)
    
    print("\n🐦 Twitter Trends...")
    print(json.dumps(get_twitter_trends(), indent=2))
    
    print("\n⚽ ESPN Scores...")
    print(json.dumps(get_espn_scores(), indent=2))
