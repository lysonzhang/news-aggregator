import feedparser
import json
from datetime import datetime
import hashlib  # 用于简单去重

# ==================== 1. 合法RSS源列表（2026年验证有效） ====================
RSS_SOURCES = {
    "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",                    # 全球头条
    "CNN Top Stories": "http://rss.cnn.com/rss/cnn_topstories.rss",         # CNN头条
    "CNN World": "http://rss.cnn.com/rss/cnn_world.rss",                    # 国际新闻
    "CNN Business": "http://rss.cnn.com/rss/money_latest.rss",              # 财金专区（助力分类）
    "CNN Tech": "http://rss.cnn.com/rss/cnn_tech.rss",                      # 科技专区（助力分类）
}

# ==================== 2. 分类关键词（英文为主，适配国际通讯社） ====================
def get_category(title: str, summary: str) -> str:
    text = (title + " " + summary).lower()
    if any(kw in text for kw in ["tech", "ai", "5g", "smartphone", "chip", "science", "gadget", "electric car", "software"]):
        return "科技"
    elif any(kw in text for kw in ["finance", "stock", "economy", "market", "business", "money", "wall street", "crypto", "inflation"]):
        return "财金"
    elif any(kw in text for kw in ["health", "education", "housing", "social", "life", "people", "welfare", "medical", "daily life"]):
        return "民生"
    else:
        return "实时热点"  # 默认或突发新闻

# ==================== 3. 采集主函数 ====================
def fetch_news():
    all_news = []
    seen_links = set()  # 防重复
    
    for name, url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                print(f"⚠️ {name} 源暂无数据，跳过")
                continue
                
            for entry in feed.entries[:8]:  # 每个源限取前8条，避免过多
                link = entry.link
                if link in seen_links:
                    continue
                seen_links.add(link)
                
                title = entry.title.strip()
                summary = entry.get("summary", "") or entry.get("description", "")[:300]
                pub_date = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub_date:
                    pub_date = datetime(*pub_date[:6]).isoformat()
                else:
                    pub_date = datetime.now().isoformat()
                
                category = get_category(title, summary)
                
                all_news.append({
                    "source": name,
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "date": pub_date,
                    "category": category
                })
        except Exception as e:
            print(f"❌ {name} 采集失败: {e}（可能是临时网络问题）")
    
    # 按日期倒序排序
    all_news.sort(key=lambda x: x["date"], reverse=True)
    return all_news

# ==================== 4. 执行并保存 ====================
if __name__ == "__main__":
    print("🚀 开始采集全球通讯社RSS新闻...")
    news_data = fetch_news()
    
    # 保存JSON（供后续网页读取）
    output = {
        "update_time": datetime.now().isoformat(),
        "total": len(news_data),
        "news": news_data
    }
    with open("latest_news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # 分类统计打印（便于检查）
    from collections import Counter
    cats = Counter(item["category"] for item in news_data)
    print(f"✅ 采集完成！共 {len(news_data)} 条新闻")
    print("📊 分类分布：", dict(cats))
    print("📁 文件已保存为 latest_news.json（可直接用于网页）")
