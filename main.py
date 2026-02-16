#!/usr/bin/env python3
"""
TRP Bot - Main Entry Point
Data ingestion for AI-powered EPL podcast
"""

import json
from datetime import datetime
from match_fetcher import fetch_matches, get_current_epl_table, fetch_match_details
from reddit_scraper import fetch_reddit_buzz, extract_topics

def run_daily_ingestion(date=None):
    """
    Run full daily data ingestion:
    1. Get today's matches
    2. Get table standings
    3. Get Reddit buzz
    4. Extract trending topics
    """
    print("=" * 50)
    print(f"TRP Bot - Daily Ingestion")
    print(f"Date: {date or datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 50)
    
    report = {
        "ingestion_date": datetime.now().isoformat(),
        "matches": {},
        "table": {},
        "buzz": {},
        "topics": {}
    }
    
    # 1. Fetch today's matches
    print("\n📅 Fetching matches...")
    matches = fetch_matches()
    if "error" not in matches:
        report["matches"] = matches
        print(f"   Found {matches.get('count', 0)} matches")
        for m in matches.get("matches", []):
            status = m.get("status", "UNKNOWN")
            print(f"   - {m['home_team']} vs {m['away_team']}: {m['home_score']}-{m['away_score']} [{status}]")
    else:
        print(f"   Error: {matches['error']}")
    
    # 2. Fetch league table
    print("\n📊 Fetching table...")
    table = get_current_epl_table()
    if "error" not in table:
        report["table"] = table
        print("   Top 5:")
        for t in table.get("table", [])[:5]:
            print(f"   {t['position']}. {t['team']} - {t['points']} pts")
    else:
        print(f"   Error: {table['error']}")
    
    # 3. Fetch Reddit buzz
    print("\n🔥 Fetching Reddit buzz...")
    buzz = fetch_reddit_buzz()
    if "error" not in buzz:
        report["buzz"] = buzz
        print(f"   Got {len(buzz.get('posts', []))} posts")
    else:
        print(f"   Error: {buzz.get('error')}")
    
    # 4. Extract topics
    if "posts" in buzz:
        print("\n🎯 Extracting topics...")
        topics = extract_topics(buzz)
        report["topics"] = topics
        
        print("   By category:")
        for cat, ts in topics.get("by_category", {}).items():
            if ts:
                print(f"   - {cat}: {len(ts)} posts")
        
        print("\n   Top 5 trending:")
        for t in topics.get("topics", [])[:5]:
            print(f"   [{t['category']}] {t['title'][:50]}...")
    
    # Save report
    filename = f"ingestion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n💾 Saved to {filename}")
    
    return report

def generate_prompt_context(report):
    """
    Generate context for AI script generation from ingestion report
    """
    context = """
# EPL Weekly Digest - AI Podcast Context

## Today's Matches
"""
    for m in report.get("matches", {}).get("matches", []):
        context += f"- {m['home_team']} {m['home_score']} - {m['away_score']} {m['away_team']} ({m.get('status')})\n"
    
    context += """
## League Table (Top 10)
"""
    for t in report.get("table", {}).get("table", [])[:10]:
        context += f"{t['position']}. {t['team']} - {t['points']}pts ({t['played']} played)\n"
    
    context += """
## Trending Topics (from Reddit)
"""
    for t in report.get("topics", {}).get("topics", [])[:10]:
        context += f"- [{t['category']}] {t['title']}\n"
    
    return context

if __name__ == "__main__":
    report = run_daily_ingestion()
    
    print("\n" + "=" * 50)
    print("Generated AI Context:")
    print("=" * 50)
    print(generate_prompt_context(report))
