import os
import json
import requests
from bs4 import BeautifulSoup

GIST_ID = "e269fe94e14da306ca248e04d8960ae3"
GIST_FILENAME = "events.json"
GITHUB_TOKEN = os.environ.get("GIST_TOKEN")

URL = "https://gwww.gnjoy.hk/sea_official/list.html?srtl=3284.0.0.0&language=en-US"

def scrape_announcements():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(URL, headers=headers)
    
    if response.status_code != 200:
        print("Failed to fetch page")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    announcements = []

    # Subukan nating hanapin ang lahat ng posibleng list items o news links sa page
    items = soup.find_all(['li', 'div'], class_=['news-item', 'item'])
    if not items:
        # Fallback kung generic tags lang ang available
        items = soup.find_all('li')

    for index, item in enumerate(items[:10], start=1):
        title_element = item.find('a')
        date_element = item.find(['span', 'p', 'div'])
        
        if title_element:
            title = title_element.get_text(strip=True)
            link = title_element.get('href', '')
            date = date_element.get_text(strip=True) if date_element else "Recent"
            
            if title and len(title) > 3: # Siguraduhing may laman ang pamagat
                announcements.append({
                    "id": str(index),
                    "title": title,
                    "date": date,
                    "link": link,
                    "content": f"Official Ragnarok update: {title}"
                })

    return announcements

def update_gist(news_data):
    if not news_data:
        print("Walang nakuhang data mula sa scraping.")
        return

    payload_data = {
        "news": news_data,
        "events": [] 
    }

    gist_data = {
        "files": {
            GIST_FILENAME: {
                "content": json.dumps(payload_data, indent=2, ensure_ascii=False)
            }
        }
    }
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json=gist_data)
    
    if response.status_code == 200:
        print("Gist updated successfully!")
    else:
        print(f"Failed to update Gist: {response.text}")

if __name__ == "__main__":
    data = scrape_announcements()
    if data:
        update_gist(data)
