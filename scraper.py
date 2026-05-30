import feedparser
from bs4 import BeautifulSoup

CATEGORY_FEEDS = [
    ("Colombia",   "https://www.eltiempo.com/rss/colombia.xml"),
    ("Política",   "https://www.eltiempo.com/rss/politica_y_justicia.xml"),
    ("Economía",   "https://www.eltiempo.com/rss/economia_y_negocios.xml"),
    ("Deportes",   "https://www.eltiempo.com/rss/deportes.xml"),
    ("Mundo",      "https://www.eltiempo.com/rss/mundo.xml"),
    ("Vida",       "https://www.eltiempo.com/rss/vida_y_ocio.xml"),
    ("Tecnología", "https://www.eltiempo.com/rss/tecnosfera.xml"),
]

ARTICLES_PER_CATEGORY = 2


def get_top_news():
    articles = []
    rank = 1
    for category, url in CATEGORY_FEEDS:
        feed = feedparser.parse(url)
        count = 0
        for entry in feed.entries:
            if count >= ARTICLES_PER_CATEGORY:
                break
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = BeautifulSoup(entry.get("summary", ""), "html.parser").get_text(strip=True)
            if not title or not link or len(summary) < 30:
                continue
            articles.append({
                "rank": rank,
                "category": category,
                "title": title,
                "url": link,
                "summary": summary,
            })
            rank += 1
            count += 1
    return articles
