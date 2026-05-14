import feedparser
import json
import re
from datetime import datetime

def clean_html(raw_html):
    if not raw_html: return ""
    return re.sub('<.*?>', '', raw_html)[:150]

with open('settings.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

news_results = {cat: [] for cat in config['categories']}

for url in config['sources']:
    feed = feedparser.parse(url)
    source_name = feed.feed.get('title', '新聞源')
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        summary = clean_html(entry.get('summary', ''))
        
        for cat, keywords in config['categories'].items():
            if any(k in title or k in summary for k in keywords):
                news_results[cat].append({
                    "title": title,
                    "link": link,
                    "source": source_name,
                    "summary": summary,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                break

# 確保每個分類不會過多，維持效能
for cat in news_results:
    news_results[cat] = news_results[cat][:30]

with open('news_data.json', 'w', encoding='utf-8') as f:
    json.dump(news_results, f, ensure_ascii=False, indent=2)
