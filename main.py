import sys
from scraper import get_top_news
from summarizer import rank_and_summarize
from email_sender import send_email

RECIPIENT = "lbotero@gmail.com"
NUM_ARTICLES = 10
FETCH_EXTRA = 15  # Fetch more than needed so the ranker has choices


def main():
    print("Fetching news from El Tiempo...")
    articles = get_top_news(FETCH_EXTRA)
    if not articles:
        print("ERROR: No articles fetched. Aborting.", file=sys.stderr)
        sys.exit(1)
    print(f"  Fetched {len(articles)} articles.")

    print("Ranking and summarizing with Claude...")
    summarized = rank_and_summarize(articles, top_n=NUM_ARTICLES)
    print(f"  Ranked and summarized {len(summarized)} articles.")

    print(f"Sending email to {RECIPIENT}...")
    send_email(summarized, RECIPIENT)
    print("Done.")


if __name__ == "__main__":
    main()
