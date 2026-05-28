def rank_and_summarize(articles, top_n=10):
    result = []
    for i, article in enumerate(articles[:top_n]):
        summary = article.get("summary") or article.get("content", "")[:300]
        result.append({
            "rank": i + 1,
            "title": article["title"],
            "url": article["url"],
            "summary": summary,
        })
    return result
