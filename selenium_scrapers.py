# TRP Bot - Selenium Scrapers
# For JS-rendered sites (BBC, Sky Sports)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import requests
import json

def get_chrome_driver():
    """Set up Chrome driver for ARM64"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
    
    # Use snap chromium
    options.binary_location = "/snap/chromium/current/usr/lib/chromium-browser/chromium-browser"
    
    try:
        # Try with webdriver-manager
        service = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        driver = webdriver.Chrome(options=options, service=Service(service))
        return driver
    except Exception as e:
        print(f"ChromeDriver manager failed: {e}")
        
        # Fallback: try direct
        try:
            service = Service("/snap/chromium/3312/usr/lib/chromium-browser/chromedriver")
            driver = webdriver.Chrome(options=options, service=service)
            return driver
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            return None

def get_bbc_live_scores_selenium():
    """Get live scores from BBC using Selenium"""
    driver = get_chrome_driver()
    if not driver:
        return {"error": "Could not initialize Chrome"}
    
    try:
        driver.get("https://www.bbc.com/sport/football/premier-league/scores")
        
        # Wait for content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
        )
        
        matches = []
        
        # Find match blocks
        match_blocks = driver.find_elements(By.CSS_SELECTOR, "article")
        for block in match_blocks[:10]:
            try:
                title = block.find_element(By.CSS_SELECTOR, "h3").text
                if "vs" in title:
                    matches.append(title)
            except:
                pass
        
        return {"source": "BBC (Selenium)", "matches": matches}
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        driver.quit()

def get_sky_sports_news_selenium():
    """Get news from Sky Sports using Selenium"""
    driver = get_chrome_driver()
    if not driver:
        return {"error": "Could not initialize Chrome"}
    
    try:
        driver.get("https://www.skysports.com/football/news")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".news-list__link"))
        )
        
        articles = []
        links = driver.find_elements(By.CSS_SELECTOR, ".news-list__link")[:15]
        
        for link in links:
            try:
                title = link.get_attribute("title") or link.text
                if title and len(title) > 10:
                    articles.append({
                        "title": title.strip()[:100],
                        "url": link.get_attribute("href")
                    })
            except:
                pass
        
        return {"source": "Sky Sports (Selenium)", "articles": articles}
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        driver.quit()

def get_flashscore_live_selenium():
    """Get live scores from Flashscore"""
    driver = get_chrome_driver()
    if not driver:
        return {"error": "Could not initialize Chrome"}
    
    try:
        driver.get("https://www.flashscore.com/football/england/premier-league/")
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_Selector, ".league__table"))
        )
        
        # Get match data
        matches = []
        match_elements = driver.find_elements(By.CSS_SELECTOR, ".event__match")[:20]
        
        for match in match_elements:
            try:
                home = match.find_element(By.CSS_SELECTOR, ".event__home").text
                away = match.find_element(By.CSS_SELECTOR, ".event__away").text
                score = match.find_element(By.CSS_SELECTOR, ".event__score").text
                time = match.find_element(By.CSS_SELECTOR, ".event__time").text
                
                matches.append({
                    "home": home,
                    "away": away,
                    "score": score,
                    "time": time
                })
            except:
                pass
        
        return {"source": "Flashscore (Selenium)", "matches": matches}
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Testing Selenium scrapers...")
    print("This may take a while on first run...")
    
    print("\n📰 BBC Scores...")
    result = get_bbc_live_scores_selenium()
    print(json.dumps(result, indent=2)[:500] if "error" not in result else result)
