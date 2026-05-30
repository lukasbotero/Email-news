import sys
from scraper import get_top_news
from email_sender import send_email

RECIPIENT = "lbotero@gmail.com"
NUM_ARTICLES = 10


def main():
    print("Fetching news from El Tiempo...")
    articles = get_top_news()
    if not articles:
        print("ERROR: No articles fetched. Aborting.", file=sys.stderr)
        sys.exit(1)
    print(f"  Fetched {len(articles)} articles.")

    print(f"Sending email to {RECIPIENT}...")
    send_email(articles, RECIPIENT)
    print("Done.")


if __name__ == "__main__":
    main()
