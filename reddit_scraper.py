# TRP Bot - Social Buzz Scraper
# Fetches trending topics from Reddit

import requests
import json
from datetime import datetime, timedelta
import os

# Reddit API - get credentials at https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = "TRP-Bot/1.0 (EPL Podcast Project)"

# Subreddits to track
EPL_SUBREDDITS = [
    "soccer",
    "PremierLeague",
    "FantasyPL",
    "football",
    "coys",        # Tottenham
    "LiverpoolFC",
    "Gunners",
    "MCFC",        # Man City
    "reddevils",   # Man Utd
    "ChelseaFC",
    "Everton",
    "NUFC",        # Newcastle
]

def get_access_token():
    """Get Reddit API access token"""
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        return None
    
    auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
    data = {"grant_type": "client_credentials"}
    headers = {"User-Agent": REDDIT_USER_AGENT}
    
    try:
        response = requests.post("https://www.reddit.com/api/v1/access_token", 
                               auth=auth, data=data, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["access_token"]
    except:
        return None

def fetch_subreddit_posts(subreddit, limit=25, sort="hot"):
    """
    Fetch posts from a subreddit
    sort: hot, new, top, rising
    """
    token = get_access_token()
    
    if not token:
        # Fallback to no-auth requests (more limited)
        url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
        headers = {"User-Agent": REDDIT_USER_AGENT}
    else:
        url = f"https://oauth.reddit.com/r/{subreddit}/{sort}"
        headers = {
            "User-Agent": REDDIT_USER_AGENT,
            "Authorization": f"Bearer {token}"
        }
    
    params = {"limit": limit, "t": "week"}  # Past week's top posts
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return parse_posts(data)
    except Exception as e:
        return {"error": str(e), "subreddit": subreddit}

def parse_posts(data):
    """Parse Reddit API response"""
    posts = []
    
    children = data.get("data", {}).get("children", [])
    
    for post in children:
        p = post.get("data", {})
        posts.append({
            "id": p.get("id"),
            "title": p.get("title"),
            "selftext": p.get("selftext")[:500] if p.get("selftext") else "",
            "subreddit": p.get("subreddit"),
            "score": p.get("score"),
            "num_comments": p.get("num_comments"),
            "url": p.get("url"),
            "created_utc": p.get("created_utc"),
            "permalink": p.get("permalink")
        })
    
    return posts

def fetch_reddit_buzz(teams=None):
    """
    Fetch trending posts across EPL subreddits
    teams: optional list of teams to filter for
    """
    all_posts = []
    
    for subreddit in EPL_SUBREDDITS:
        if teams:
            # Skip if not a team-specific sub and teams specified
            team_subs = ["coys", "LiverpoolFC", "Gunners", "MCFC", "reddevils", "ChelseaFC", "Everton", "NUFC"]
            if subreddit not in team_subs:
                continue
        
        result = fetch_subreddit_posts(subreddit, limit=15)
        if isinstance(result, list):
            all_posts.extend(result)
    
    # Sort by score
    all_posts.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    return {
        "source": "Reddit",
        "subreddits": EPL_SUBREDDITS,
        "posts": all_posts[:50],  # Top 50
        "fetched_at": datetime.now().isoformat()
    }

def get_post_comments(post_permalink):
    """Get top comments from a specific post"""
    token = get_access_token()
    
    if token:
        url = f"https://oauth.reddit.com{post_permalink}"
        headers = {
            "User-Agent": REDDIT_USER_AGENT,
            "Authorization": f"Bearer {token}"
        }
    else:
        url = f"https://www.reddit.com{post_permalink}.json"
        headers = {"User-Agent": REDDIT_USER_AGENT}
    
    params = {"limit": 10}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        comments = []
        for child in data[1]["data"]["children"]:
            c = child["data"]
            comments.append({
                "author": c.get("author"),
                "body": c.get("body")[:300],
                "score": c.get("score"),
                "is_op": c.get("is_original_content")
            })
        
        return comments[:10]
    except Exception as e:
        return [{"error": str(e)}]

def extract_topics(buzz_data):
    """
    Extract trending topics from Reddit buzz
    Returns list of topics with engagement metrics
    """
    topics = {}
    
    keywords_goals = ["goal", "score", "miss", "chance", "shot"]
    keywords_controversy = ["referee", "var", "penalty", "foul", "red card"]
    keywords_transfer = ["transfer", "sign", "rumor", "contract"]
    keywords_manager = ["manager", "coach", "tactics", "formation"]
    
    for post in buzz_data.get("posts", []):
        title = post.get("title", "").lower()
        score = post.get("score", 0)
        comments = post.get("num_comments", 0)
        engagement = score + comments * 2  # Weight comments
        
        # Categorize
        category = "general"
        if any(k in title for k in keywords_goals):
            category = "match_action"
        elif any(k in title for k in keywords_controversy):
            category = "controversy"
        elif any(k in title for k in keywords_transfer):
            category = "transfer"
        elif any(k in title for k in keywords_manager):
            category = "tactics"
        
        topics[post["id"]] = {
            "title": post["title"],
            "subreddit": post["subreddit"],
            "score": score,
            "comments": comments,
            "engagement": engagement,
            "category": category,
            "url": f"https://reddit.com{post['permalink']}"
        }
    
    # Sort by engagement
    sorted_topics = sorted(topics.values(), key=lambda x: x["engagement"], reverse=True)
    
    return {
        "topics": sorted_topics[:20],
        "by_category": {
            "match_action": [t for t in sorted_topics if t["category"] == "match_action"],
            "controversy": [t for t in sorted_topics if t["category"] == "controversy"],
            "transfer": [t for t in sorted_topics if t["category"] == "transfer"],
            "tactics": [t for t in sorted_topics if t["category"] == "tactics"],
            "general": [t for t in sorted_topics if t["category"] == "general"]
        }
    }

# Test
if __name__ == "__main__":
    print("Fetching Reddit buzz (no auth - limited)...")
    buzz = fetch_reddit_buzz()
    print(f"Got {len(buzz.get('posts', []))} posts")
    
    # Try extracting topics
    topics = extract_topics(buzz)
    print(f"\nTop topics:")
    for t in topics["topics"][:5]:
        print(f"  - [{t['category']}] {t['title'][:60]}...")
