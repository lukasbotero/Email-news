import anthropic

client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5-20251001"


def _summarize_one(title, content):
    prompt = (
        f"Resume esta noticia en español en máximo 50 palabras. "
        f"Sé conciso y captura los hechos clave.\n\n"
        f"Título: {title}\n"
        f"Contenido: {content[:2500]}\n\n"
        f"Resumen (máx. 50 palabras):"
    )
    msg = client.messages.create(
        model=MODEL,
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def rank_and_summarize(articles, top_n=10):
    """
    Use Claude to pick and rank the top_n most important articles,
    then summarize each one.
    """
    # Build a numbered list of titles + brief description for ranking
    candidates = "\n".join(
        f"{i+1}. {a['title']}"
        for i, a in enumerate(articles)
    )
    ranking_prompt = (
        f"Eres un editor de noticias colombiano. "
        f"De las siguientes noticias de El Tiempo, selecciona y ordena las {top_n} más importantes "
        f"para un lector colombiano promedio. Responde SOLO con los números en orden de importancia, "
        f"separados por comas. Ejemplo: 3,1,7,2,...\n\n"
        f"Noticias:\n{candidates}"
    )
    rank_msg = client.messages.create(
        model=MODEL,
        max_tokens=60,
        messages=[{"role": "user", "content": ranking_prompt}],
    )
    raw = rank_msg.content[0].text.strip()
    try:
        indices = [int(x.strip()) - 1 for x in raw.split(",") if x.strip().isdigit()]
        # Keep only valid indices and deduplicate
        seen = set()
        ranked = []
        for idx in indices:
            if 0 <= idx < len(articles) and idx not in seen:
                ranked.append(articles[idx])
                seen.add(idx)
        # Fill up to top_n if ranking returned fewer
        for i, a in enumerate(articles):
            if len(ranked) >= top_n:
                break
            if i not in seen:
                ranked.append(a)
    except Exception:
        ranked = articles[:top_n]

    ranked = ranked[:top_n]

    # Summarize each selected article
    result = []
    for i, article in enumerate(ranked):
        content = article.get("content", "") or article.get("summary", "")
        summary = _summarize_one(article["title"], content)
        result.append({
            "rank": i + 1,
            "title": article["title"],
            "url": article["url"],
            "summary": summary,
        })

    return result
