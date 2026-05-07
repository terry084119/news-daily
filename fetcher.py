import feedparser
import json
import re
from datetime import datetime

def clean_html(raw_html):
    if not raw_html: return ""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)[:100]

with open('settings.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

news_results = {cat: [] for cat in config['categories']}

for url in config['sources']:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        # 嘗試抓取圖片：從 media_content 或 links 中找 image
        img_url = ""
        if 'media_content' in entry:
            img_url = entry.media_content[0]['url']
        elif 'links' in entry:
            for l in entry.links:
                if 'image' in l.get('type', ''):
                    img_url = l.href
        
        # 如果沒圖片，就用一個乾淨的色塊圖代替，而不是雜亂的預設圖
        if not img_url:
            img_url = f"https://via.placeholder.com/400x250/f0f0f0/666666?text={title[:5]}"

        summary = clean_html(entry.get('summary', '點擊閱讀全文'))
        source = feed.feed.get('title', '新聞源')

        for cat, keywords in config['categories'].items():
            if any(k in title for k in keywords):
                news_results[cat].append({
                    "title": title, 
                    "link": link, 
                    "source": source, 
                    "image": img_url,
                    "summary": summary,
                    "time": datetime.now().strftime("%m/%d %H:%M")
                })
                break

with open('news_data.json', 'w', encoding='utf-8') as f:
    json.dump(news_results, f, ensure_ascii=False, indent=2)
