import feedparser
import json
from datetime import datetime

with open('settings.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

news_results = {cat: [] for cat in config['categories']}

for url in config['sources']:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        source = feed.feed.get('title', '新聞源')
        for cat, keywords in config['categories'].items():
            if any(k in title for k in keywords):
                news_results[cat].append({"title": title, "link": link, "source": source, "time": datetime.now().strftime("%m/%d %H:%M")})
                break

with open('news_data.json', 'w', encoding='utf-8') as f:
    json.dump(news_results, f, ensure_ascii=False, indent=2)
