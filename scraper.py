import os
import json
import requests
from bs4 import BeautifulSoup

# Palitan ito ng iyong aktwal na Gist ID at Filename
GIST_ID = "e269fe94e14da306ca248e04d8960ae3"
GIST_FILENAME = "events.json"
GITHUB_TOKEN = os.environ.get("GIST_TOKEN")

URL = "https://gwww.gnjoy.hk/sea_official/list.html?srtl=3284.0.0.0&language=en-US"

def scrape_announcements():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    
    if response.status_code != 200:
        print("Failed to fetch page")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    announcements = []

    items = soup.find_all('li')
    
    for item in items[:10]:
        title_element = item.find('a')
        date_element = item.find('span')
        
        if title_element:
            title = title_element.get_text(strip=True)
            link = title_element.get('href', '')
            date = date_element.get_text(strip=True) if date_element else ""
            
            announcements.append({
                "title": title,
                "date": date,
                "link": link
            })

    return announcements

def update_gist(data):
    if not data:
        print("No data to update.")
        return

    gist_data = {
        "files": {
            GIST_FILENAME: {
                "content": json.dumps(data, indent=2, ensure_ascii=False)
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
