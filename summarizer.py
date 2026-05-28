import os
import json
from google import genai

MODEL = "gemini-2.0-flash-lite"


def rank_and_summarize(articles, top_n=10):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    candidates = "\n".join(
        f"{i+1}. {a['title']} | {(a.get('content') or a.get('summary', ''))[:300]}"
        for i, a in enumerate(articles)
    )

    prompt = (
        f"Eres un editor de noticias colombiano. "
        f"Tienes las siguientes noticias de El Tiempo. "
        f"Selecciona las {top_n} más importantes para un lector colombiano promedio, "
        f"incluyendo distintas categorías (política, economía, deportes, cultura, etc.). "
        f"Excluye columnas de opinión, promociones o contenido que no sea noticia real.\n\n"
        f"Para cada noticia seleccionada, escribe un resumen en español de máximo 50 palabras.\n\n"
        f"Responde ÚNICAMENTE con un JSON válido con este formato:\n"
        f'[{{"rank": 1, "index": 3, "summary": "..."}}, ...]\n\n'
        f"Noticias:\n{candidates}"
    )

    response = client.models.generate_content(model=MODEL, contents=prompt)
    raw = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        ranked = json.loads(raw)
    except Exception:
        return [
            {"rank": i + 1, "title": a["title"], "url": a["url"],
             "summary": a.get("summary") or a.get("content", "")[:200]}
            for i, a in enumerate(articles[:top_n])
        ]

    result = []
    for item in ranked[:top_n]:
        idx = item.get("index", 1) - 1
        if 0 <= idx < len(articles):
            article = articles[idx]
        else:
            continue
        result.append({
            "rank": item.get("rank", len(result) + 1),
            "title": article["title"],
            "url": article["url"],
            "summary": item.get("summary", ""),
        })

    return result
