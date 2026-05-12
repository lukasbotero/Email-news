import time
import requests
import xml.etree.ElementTree as ET
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

RSS_URLS = [
    "https://www.eltiempo.com/rss/portada.xml",
    "https://www.eltiempo.com/rss/colombia.xml",
    "https://www.eltiempo.com/rss/nacion.xml",
]
# Google News RSS as last-resort fallback (links back to El Tiempo articles)
GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search"
    "?q=site:eltiempo.com&hl=es-419&gl=CO&ceid=CO:es-419"
)
HOME_URL = "https://www.eltiempo.com"


def _parse_rss_xml(content):
    root = ET.fromstring(content)
    channel = root.find("channel")
    items = channel.findall("item") if channel is not None else root.findall(".//item")
    articles = []
    for item in items:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = item.findtext("description") or ""
        summary = BeautifulSoup(description, "html.parser").get_text(strip=True)
        if title and link:
            articles.append({"title": title, "url": link, "summary": summary})
    return articles


def _fetch_via_rss(limit=15):
    for rss_url in RSS_URLS:
        try:
            resp = requests.get(rss_url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            articles = _parse_rss_xml(resp.content)
            if articles:
                return articles[:limit]
        except Exception:
            continue

    # Last resort: Google News RSS for El Tiempo
    try:
        resp = requests.get(GOOGLE_NEWS_RSS, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return _parse_rss_xml(resp.content)[:limit]
    except Exception:
        return []


def _fetch_via_html(limit=15):
    resp = requests.get(HOME_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    seen_urls = set()
    articles = []

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
