import time
import requests
import feedparser
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

RSS_URL = "https://www.eltiempo.com/rss/portada.xml"
HOME_URL = "https://www.eltiempo.com"


def _fetch_via_rss(limit=15):
    feed = feedparser.parse(RSS_URL)
    articles = []
    for entry in feed.entries[:limit]:
        articles.append({
            "title": entry.get("title", "").strip(),
            "url": entry.get("link", ""),
            "summary": BeautifulSoup(entry.get("summary", ""), "html.parser").get_text(strip=True),
        })
    return articles


def _fetch_via_html(limit=15):
    resp = requests.get(HOME_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    seen_urls = set()
    articles = []

    # Try common article link patterns on eltiempo.com
    selectors = [
        "article a[href]",
        "h2 a[href]",
        "h3 a[href]",
        ".title a[href]",
        "[class*='article'] a[href]",
        "[class*='news'] a[href]",
    ]
    for sel in selectors:
        for tag in soup.select(sel):
            href = tag.get("href", "")
            if not href:
                continue
            if href.startswith("/"):
                href = HOME_URL + href
            if href in seen_urls or HOME_URL not in href:
                continue
            # Skip non-article URLs (section index pages, etc.)
            if href.count("/") < 4:
                continue
            title = tag.get_text(strip=True)
            if len(title) < 15:
                continue
            seen_urls.add(href)
            articles.append({"title": title, "url": href, "summary": ""})
            if len(articles) >= limit:
                return articles

    return articles


def fetch_article_text(url, max_chars=3000):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        # Prefer the <article> body
        body = (
            soup.find("article")
            or soup.find(class_=lambda c: c and any(
                k in c for k in ("article-body", "content-body", "nota", "article-content")
            ))
        )
        text = (body or soup).get_text(separator=" ", strip=True)
        return text[:max_chars]
    except Exception:
        return ""


def get_top_news(n=10):
    """Return up to n articles with content fetched."""
    # Try RSS first; fall back to HTML scraping
    articles = _fetch_via_rss(limit=n + 5)
    if len(articles) < 3:
        articles = _fetch_via_html(limit=n + 5)

    result = []
    for article in articles[:n + 5]:
        if not article["url"] or not article["title"]:
            continue
        content = fetch_article_text(article["url"])
        article["content"] = content
        result.append(article)
        time.sleep(0.5)
        if len(result) >= n:
            break

    return result
