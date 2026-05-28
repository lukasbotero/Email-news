import os
from google import genai

MODEL = "gemini-2.0-flash"


def _get_client():
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def _summarize_one(client, title, content):
    prompt = (
        f"Resume esta noticia en español en máximo 50 palabras. "
        f"Sé conciso y captura los hechos clave.\n\n"
        f"Título: {title}\n"
        f"Contenido: {content[:2500]}\n\n"
        f"Resumen (máx. 50 palabras):"
    )
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text.strip()


def rank_and_summarize(articles, top_n=10):
    client = _get_client()

    candidates = "\n".join(
        f"{i+1}. {a['title']}"
        for i, a in enumerate(articles)
    )
    ranking_prompt = (
        f"Eres un editor de noticias colombiano. "
        f"De las siguientes noticias de El Tiempo, selecciona y ordena las {top_n} más importantes "
        f"para un lector colombiano promedio. Incluye noticias de distintas categorías (política, economía, "
        f"deportes, cultura, etc.). Excluye columnas de opinión, promociones o contenido que no sea noticia. "
        f"Responde SOLO con los números en orden de importancia, separados por comas. Ejemplo: 3,1,7,2,...\n\n"
        f"Noticias:\n{candidates}"
    )
    rank_response = client.models.generate_content(model=MODEL, contents=ranking_prompt)
    raw = rank_response.text.strip()

    try:
        indices = [int(x.strip()) - 1 for x in raw.split(",") if x.strip().isdigit()]
        seen = set()
        ranked = []
        for idx in indices:
            if 0 <= idx < len(articles) and idx not in seen:
                ranked.append(articles[idx])
                seen.add(idx)
        for i, a in enumerate(articles):
            if len(ranked) >= top_n:
                break
            if i not in seen:
                ranked.append(a)
    except Exception:
        ranked = articles[:top_n]

    ranked = ranked[:top_n]

    result = []
    for i, article in enumerate(ranked):
        content = article.get("content", "") or article.get("summary", "")
        summary = _summarize_one(client, article["title"], content)
        result.append({
            "rank": i + 1,
            "title": article["title"],
            "url": article["url"],
            "summary": summary,
        })

    return result
