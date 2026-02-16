# TRP Bot - Match Data Fetcher
# Fetches EPL match events, stats, and commentary

import requests
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os

# Config - set your API keys here
FOOTBALL_DATA_API_KEY = os.environ.get("FOOTBALL_DATA_API_KEY", "")  # Get from football-data.org
BBC_MATCH_URL = "https://www.bbc.com/sport/football/live"  # Live scores page

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
}

def get_comp_id(competition="PL"):
    """Map competition name to ID"""
    comps = {
        "PL": 2021,      # Premier League
        "CL": 2001,      # Champions League
        "EL": 2013,     # Europa League
        "FA": 2014,     # FA Cup
        "EFL": 2015,   # Carabao Cup
    }
    return comps.get(competition, 2021)

def fetch_matches(date=None, competition="PL"):
    """
    Fetch matches for a specific date
    date: datetime object or None for today
    """
    if not FOOTBALL_DATA_API_KEY:
        return {"error": "No API key set. Get one at https://football-data.org"}
    
    if date is None:
        date = datetime.now()
    
    date_str = date.strftime("%Y-%m-%d")
    
    url = f"https://api.football-data-org-api.com/v4/matches"
    params = {
        "dateFrom": date_str,
        "dateTo": date_str,
        "competitions": get_comp_id(competition)
    }
    headers = {
        "X-Auth-Token": FOOTBALL_DATA_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return parse_matches(data)
    except Exception as e:
        return {"error": str(e)}

def parse_matches(data):
    """Parse API response into clean format"""
    matches = []
    
    if "matches" not in data:
        return {"error": "No matches found", "raw": data}
    
    for match in data["matches"]:
        match_info = {
            "id": match.get("id"),
            "home_team": match["homeTeam"]["name"],
            "away_team": match["awayTeam"]["name"],
            "home_score": match["score"]["fullTime"]["home"],
            "away_score": match["score"]["fullTime"]["away"],
            "status": match["status"],  # SCHEDULED, IN_PLAY, FINISHED, etc.
            "kickoff": match.get("kickoffTime"),
            "competition": match["competition"]["name"],
            "venue": match.get("venue"),
            "events": [],
            "stats": {}
        }
        
        # Parse events if available
        if match.get("odds"):
            # Odds data sometimes available
            pass
            
        matches.append(match_info)
    
    return {
        "date": data.get("matches", [{}])[0].get("utcDate", "")[:10] if matches else "",
        "count": len(matches),
        "matches": matches
    }

def fetch_match_details(match_id):
    """Fetch detailed match info including events"""
    if not FOOTBALL_DATA_API_KEY:
        return {"error": "No API key set"}
    
    url = f"https://api.football-data-org-api.com/v4/matches/{match_id}"
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return parse_match_details(data)
    except Exception as e:
        return {"error": str(e)}

def parse_match_details(data):
    """Parse detailed match data"""
    match = data
    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]
    
    details = {
        "match": f"{home} vs {away}",
        "score": f"{match['score']['fullTime']['home']} - {match['score']['fullTime']['away']}",
        "status": match["status"],
        "events": [],
        "stats": {}
    }
    
    # Parse events
    if "matchEvents" in data:
        for event in data["matchEvents"]:
            event_data = {
                "minute": event.get("minute"),
                "type": event.get("type"),  # GOAL, SUBSTITUTION, CARD, etc.
                "player": event.get("player", {}).get("name"),
                "detail": event.get("detail"),
                "team": event["team"]["name"] if "team" in event else None
            }
            details["events"].append(event_data)
    
    # Sort events by minute
    details["events"].sort(key=lambda x: x["minute"] or 0)
    
    return details

def scrape_bbc_commentary(match_url):
    """
    Scrape live text commentary from BBC
    match_url: e.g., "https://www.bbc.com/sport/football/68012345"
    """
    try:
        response = requests.get(match_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # BBC live commentary structure changes often, this is a basic version
        commentary = []
        
        # Try to find match summary
        summary = soup.find("div", {"data-component": "match-summary"})
        if summary:
            details = summary.find_all("p")
            for d in details:
                commentary.append(d.text.strip())
        
        # Try alternative structure
        if not commentary:
            posts = soup.find_all("article", {"class": "ssrcss-1w5ebf-Article"})
            for post in posts:
                time = post.find("time")
                text = post.find("p")
                if time and text:
                    commentary.append({
                        "time": time.text,
                        "text": text.text.strip()
                    })
        
        return {
            "source": "BBC",
            "url": match_url,
            "commentary": commentary[:50]  # Limit to 50 entries
        }
    except Exception as e:
        return {"error": str(e)}

def get_current_epl_table():
    """Fetch current Premier League table"""
    if not FOOTBALL_DATA_API_KEY:
        return {"error": "No API key"}
    
    url = "https://api.football-data-org-api.com/v4/competitions/2021/standings"
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        table = []
        for team in data["standings"][0]["table"]:
            table.append({
                "position": team["position"],
                "team": team["team"]["name"],
                "played": team["playedGames"],
                "won": team["won"],
                "drawn": team["drawn"],
                "lost": team["lost"],
                "gd": team["goalDifference"],
                "points": team["points"]
            })
        
        return {"table": table}
    except Exception as e:
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    # Test without API key first
    print("Testing match fetch (no API key)...")
    result = fetch_matches()
    print(json.dumps(result, indent=2))
