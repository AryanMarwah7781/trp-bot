# TRP Bot - Playwright Scrapers
# For JS-rendered sites (BBC, Sky Sports, Flashscore)

from playwright.sync_api import sync_playwright
import json

def get_bbc_live_scores():
    """Get live scores from BBC using Playwright"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.bbc.com/sport/football/premier-league/scores", wait_until="networkidle")
            
            # Wait for content
            page.wait_for_selector("article", timeout=10000)
            
            matches = []
            articles = page.query_selector_all("article")[:15]
            
            for article in articles:
                try:
                    title = article.query_selector("h3")
                    if title and "vs" in title.inner_text():
                        matches.append(title.inner_text())
                except:
                    pass
            
            browser.close()
            return {"source": "BBC (Playwright)", "matches": matches}
    except Exception as e:
        return {"error": str(e)}

def get_sky_sports_news():
    """Get news from Sky Sports using Playwright"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.skysports.com/football/news", wait_until="networkidle")
            
            page.wait_for_selector(".news-list__link", timeout=10000)
            
            articles = []
            links = page.query_selector_all(".news-list__link")[:15]
            
            for link in links:
                try:
                    title = link.get_attribute("title") or link.inner_text()
                    if title and len(title.strip()) > 10:
                        articles.append({
                            "title": title.strip()[:100],
                            "url": link.get_attribute("href")
                        })
                except:
                    pass
            
            browser.close()
            return {"source": "Sky Sports (Playwright)", "articles": articles}
    except Exception as e:
        return {"error": str(e)}

def get_flashscore_live():
    """Get live scores from Flashscore"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.flashscore.com/football/england/premier-league/", wait_until="networkidle")
            
            page.wait_for_selector(".event__match", timeout=15000)
            
            matches = []
            events = page.query_selector_all(".event__match")[:20]
            
            for event in events:
                try:
                    home = event.query_selector(".event__home")
                    away = event.query_selector(".event__away")
                    score = event.query_selector(".event__score")
                    time = event.query_selector(".event__time")
                    
                    if home and away:
                        matches.append({
                            "home": home.inner_text(),
                            "away": away.inner_text(),
                            "score": score.inner_text() if score else "",
                            "time": time.inner_text() if time else ""
                        })
                except:
                    pass
            
            browser.close()
            return {"source": "Flashscore (Playwright)", "matches": matches}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("Testing Playwright scrapers...")
    
    print("\n📰 BBC Scores...")
    r = get_bbc_live_scores()
    print(json.dumps(r, indent=2)[:800] if "error" not in r else r)
    
    print("\n📰 Sky Sports...")
    r2 = get_sky_sports_news()
    print(json.dumps(r2, indent=2)[:800] if "error" not in r2 else r2)
    
    print("\n⚽ Flashscore...")
    r3 = get_flashscore_live()
    print(json.dumps(r3, indent=2)[:800] if "error" not in r3 else r3)
