import os
import json
import feedparser
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
RSS_URL = "https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi"

os.makedirs("data", exist_ok=True)
DATA_FILE = "data/news.json"

existing_news = []
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            existing_news = json.load(f)
        except:
            existing_news = []

existing_links = {item.get("link") for item in existing_news}
feed = feedparser.parse(RSS_URL)

new_entries = []
for entry in feed.entries[:3]:  # Har baar top 3 taaza khabrein lega
    if entry.link in existing_links:
        continue

    prompt = f"""
    Is khabar ko saral aur aakarshak Hindi mein rewrite karo. 
    Title: {entry.title}
    Details: {entry.summary if 'summary' in entry else entry.title}
    
    Output kewal is shuddh JSON format mein hona chahiye (bina kisi extra text ya markdown ke bahar):
    {{"headline": "Naya aakarshak title", "summary": "60-80 shabdon ki sankshipt aur spasht summary", "category": "Tech/Sports/National aadi mein se ek", "source_name": "Google News"}}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        parsed_data = json.loads(clean_text)
        
        parsed_data["link"] = entry.link
        parsed_data["published_at"] = entry.get("published", "Aaj")
        new_entries.append(parsed_data)
    except Exception as e:
        print(f"Error: {e}")

if new_entries:
    updated_news = (new_entries + existing_news)[:50] # Maximum 50 khabrein store rahengi
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(updated_news, f, ensure_ascii=False, indent=2)
