#!/usr/bin/env python3
"""
TRP Bot - Test Run with Simulated Old Week Data
Tests the full pipeline with data from week of Jan 20-26, 2026
"""

import json
from datetime import datetime, timedelta
from reddit_scraper import fetch_reddit_buzz, extract_topics
from match_fetcher import get_current_epl_table

# Try to import YouTube scraper
try:
    from youtube_yt_dlp import get_epl_highlights
    YOUTUBE_AVAILABLE = True
except:
    # Try with different import name
    try:
        import youtube_yt_dlp as yt
        get_epl_highlights = yt.get_epl_highlights
        YOUTUBE_AVAILABLE = True
    except Exception as e:
        print(f"YouTube scraper not available: {e}")
        YOUTUBE_AVAILABLE = False

# Simulated match data for week of Jan 20-26, 2026
MOCK_MATCHES = {
    "2026-01-25": [
        {"home": "Arsenal", "away": "Chelsea", "score": "2-2", "events": [
            {"minute": 16, "type": "GOAL", "player": "Saka", "team": "Arsenal"},
            {"minute": 34, "type": "GOAL", "player": "Palmer", "team": "Chelsea"},
            {"minute": 52, "type": "GOAL", "player": "Havertz", "team": "Arsenal"},
            {"minute": 78, "type": "GOAL", "player": "Jackson", "team": "Chelsea"}
        ]},
        {"home": "Liverpool", "away": "Ipswich", "score": "4-1", "events": [
            {"minute": 12, "type": "GOAL", "player": "Salah", "team": "Liverpool"},
            {"minute": 28, "type": "GOAL", "player": "Gakpo", "team": "Liverpool"},
            {"minute": 45, "type": "GOAL", "player": "Szoboszlai", "team": "Liverpool"},
            {"minute": 67, "type": "GOAL", "player": "Nunez", "team": "Liverpool"},
            {"minute": 89, "type": "GOAL", "player": "Delap", "team": "Ipswich"}
        ]},
    ],
    "2026-01-26": [
        {"home": "Man City", "away": "Brentford", "score": "3-1", "events": [
            {"minute": 8, "type": "GOAL", "player": "Haaland", "team": "Man City"},
            {"minute": 41, "type": "GOAL", "player": "Foden", "team": "Man City"},
            {"minute": 55, "type": "GOAL", "player": "Mbeumo", "team": "Brentford"},
            {"minute": 72, "type": "GOAL", "player": "De Bruyne", "team": "Man City"}
        ]},
        {"home": "Man United", "away": "Brighton", "score": "1-0", "events": [
            {"minute": 63, "type": "GOAL", "player": "Fernandes", "team": "Man United"}
        ]},
    ]
}

# Simulated trending topics from that week
MOCK_TOPICS = [
    {"title": "Arsenal Chelsea draw - title race blown open", "category": "match_action", "score": 15420},
    {"title": "Salah scores wondergoal against Ipswich", "category": "match_action", "score": 12340},
    {"title": "Haaland back to scoring ways", "category": "match_action", "score": 8900},
    {"title": "Palmer vs Saka - who is the better winger?", "category": "general", "score": 7800},
    {"title": "VAR controversy in Arsenal vs Chelsea", "category": "controversy", "score": 11200},
    {"title": "Transfer rumor: Kane to Real Madrid", "category": "transfer", "score": 9500},
    {"title": "Slot's tactical masterclass", "category": "tactics", "score": 6700},
    {"title": " relegation battle heating up", "category": "general", "score": 5400},
]

def run_test_pipeline():
    """Run the full pipeline with test data"""
    
    print("=" * 60)
    print("TRP BOT - TEST RUN (Week of Jan 20-26, 2026)")
    print("=" * 60)
    
    # 1. Get real Reddit buzz (current)
    print("\n📡 Fetching Reddit buzz...")
    reddit_data = fetch_reddit_buzz()
    topics = extract_topics(reddit_data)
    
    print(f"   Got {len(reddit_data.get('posts', []))} posts")
    print(f"   Extracted {len(topics.get('topics', []))} topics")
    
    # 2. Get league table
    print("\n📊 Fetching league table...")
    table_result = get_current_epl_table()
    if "error" in table_result:
        print(f"   (API key needed - using mock)")
        table = get_mock_table()
    else:
        table = table_result.get("table", [])
    
    # 3. Get YouTube highlights
    print("\n📺 Fetching YouTube highlights...")
    youtube_videos = []
    if YOUTUBE_AVAILABLE:
        yt_result = get_epl_highlights(max_results=5)
        if "videos" in yt_result:
            youtube_videos = yt_result["videos"]
            print(f"   Got {len(youtube_videos)} videos")
    
    # 4. Compile the full report
    print("\n📝 Compiling weekly report...")
    
    report = {
        "week": "Jan 20-26, 2026",
        "matches": MOCK_MATCHES,
        "trending_topics": MOCK_TOPICS[:5],
        "reddit_topics": topics.get("topics", [])[:5],
        "league_table": table[:10],
        "youtube_highlights": youtube_videos,
        "generated_at": datetime.now().isoformat()
    }
    
    # 4. Generate podcast context
    print("\n🎙️ Generating podcast context...")
    context = generate_podcast_context(report)
    
    print("\n" + "=" * 60)
    print("PODCAST CONTEXT (for AI)")
    print("=" * 60)
    print(context)
    
    # Save report
    filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n💾 Saved to {filename}")
    
    return report, context

def get_mock_table():
    """Get mock league table"""
    return [
        {"position": 1, "team": "Liverpool", "played": 23, "points": 58},
        {"position": 2, "team": "Arsenal", "played": 23, "points": 52},
        {"position": 3, "team": "Man City", "played": 23, "points": 49},
        {"position": 4, "team": "Chelsea", "played": 23, "points": 45},
        {"position": 5, "team": "Newcastle", "played": 23, "points": 42},
        {"position": 6, "team": "Aston Villa", "played": 23, "points": 38},
        {"position": 7, "team": "Tottenham", "played": 23, "points": 36},
        {"position": 8, "team": "Man United", "played": 23, "points": 34},
        {"position": 9, "team": "Fulham", "played": 23, "points": 32},
        {"position": 10, "team": "Brentford", "played": 23, "points": 30},
    ]

def generate_podcast_context(report):
    """Generate the context prompt for AI script generation"""
    
    context = """# EPL WEEKLY DIGEST - AI PODCAST CONTEXT

## Week: January 20-26, 2026

## 📊 League Table (Top 10)
"""
    for team in report.get("league_table", []):
        context += f"{team['position']}. {team['team']} - {team['points']} pts ({team['played']} games)\n"
    
    context += """
## ⚽ Key Matches This Week
"""
    for date, matches in report.get("matches", {}).items():
        context += f"\n### {date}\n"
        for match in matches:
            context += f"- **{match['home']} {match['score']} {match['away']}**\n"
            for event in match.get("events", []):
                context += f"  - {event['minute']}' {event['player']} ({event['team']})\n"
    
    context += """
## 🔥 Trending Topics (from Reddit)
"""
    for t in report.get("trending_topics", []):
        context += f"- [{t['category']}] {t['title']} ({t['score']} upvotes)\n"
    
    context += """
## 🎯 AI Persona Discussion Points

1. **Title Race**: Liverpool extending their lead? Arsenal dropping points?
2. **Big Match**: Arsenal vs Chelsea 2-2 - Palmer vs Saka battle
3. **Star Performers**: Salah, Haaland scoring forms
4. **VAR Controversy**: Key decisions that sparked debate
5. **Relegation Battle**: Who's in trouble?

## 🎬 Suggested Segments

1. **Intro** (30s) - Week overview
2. **Match Recap** (3min) - Top 3 matches
3. **Deep Dive** (2min) - The big talking point
4. **Table Talk** (1min) - Title race + relegation
5. **Quick Hits** (1min) - Transfer buzz, injuries
6. **Outro** (30s) - Preview of next week

---
*Generated by TRP Bot - Data Ingestion Pipeline*
"""
    
    return context

if __name__ == "__main__":
    run_test_pipeline()
