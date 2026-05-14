import feedparser
import json
import re
import urllib.parse
from datetime import datetime, timedelta
import time

def clean_html(raw_html):
    if not raw_html: return ""
    return re.sub('<.*?>', '', raw_html)[:150]

try:
    with open('settings.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
except Exception as e:
    print(f"JSON 讀取失敗: {e}")
    exit(1)

news_results = {cat: [] for cat in config['categories']}
now = datetime.now()
one_day_ago = now - timedelta(days=1)

for cat, keywords in config['categories'].items():
    # 使用前 5 個關鍵字進行廣域搜尋
    query = " OR ".join(keywords[:5])
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    
    print(f"正在抓取【{cat}】...")
    try:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            pub_time_str = "今日新聞"
            published_parsed = entry.get('published_parsed')
            if published_parsed:
                pub_time = datetime.fromtimestamp(time.mktime(published_parsed))
                if pub_time < (now - timedelta(days=2)): continue # 保持鮮度
                pub_time_str = pub_time.strftime("%m/%d %H:%M")

            news_results[cat].append({
                "title": entry.title,
                "link": entry.link,
                "source": entry.get('source', {}).get('title', '新聞源'),
                "summary": clean_html(entry.get('summary', '')),
                "time": pub_time_str
            })
    except Exception as e:
        print(f"抓取 {cat} 失敗: {e}")

    # 去重並保留前 20 則
    seen = set()
    unique_news = []
    for n in news_results[cat]:
        if n['title'] not in seen:
            unique_news.append(n)
            seen.add(n['title'])
    news_results[cat] = unique_news[:20]

with open('news_data.json', 'w', encoding='utf-8') as f:
    json.dump(news_results, f, ensure_ascii=False, indent=2)
