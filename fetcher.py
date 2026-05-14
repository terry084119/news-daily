import feedparser
import json
import re
from datetime import datetime, timedelta
import time

def clean_html(raw_html):
    if not raw_html: return ""
    return re.sub('<.*?>', '', raw_html)[:150]

with open('settings.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

news_results = {cat: [] for cat in config['categories']}
now = datetime.now()
one_day_ago = now - timedelta(days=1)

# 擴張搜尋源：針對每個分類加入專屬的 Google News 搜尋
for cat, keywords in config['categories'].items():
    query = " OR ".join(keywords)
    # 使用 Google News RSS 確保 24 小時內的資料量
    rss_url = f"https://news.google.com/rss/search?q={query}+when:1d&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    
    feed = feedparser.parse(rss_url)
    for entry in feed.entries:
        # 檢查時間 (確保是 24 小時內)
        published_parsed = entry.get('published_parsed')
        if published_parsed:
            pub_time = datetime.fromtimestamp(time.mktime(published_parsed))
            if pub_time < one_day_ago:
                continue

        news_results[cat].append({
            "title": entry.title,
            "link": entry.link,
            "source": entry.get('source', {}).get('title', '新聞源'),
            "summary": clean_html(entry.get('summary', '')),
            "time": pub_time.strftime("%m/%d %H:%M")
        })

# 排序並去重，確保每個分類至少保留 15 則
for cat in news_results:
    # 移除重複標題
    seen = set()
    unique_news = []
    for n in news_results[cat]:
        if n['title'] not in seen:
            unique_news.append(n)
            seen.add(n['title'])
    news_results[cat] = unique_news[:15]

with open('news_data.json', 'w', encoding='utf-8') as f:
    json.dump(news_results, f, ensure_ascii=False, indent=2)
