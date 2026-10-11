
import asyncio

from services.gdelt_service import fetch_news


async def main():
    articles = await fetch_news(max_records=5)

    print(f"Articles received: {len(articles)}")

    for article in articles:
        print("\nHeadline:", article["title"])
        print("Source:", article["source"])
        print("Published:", article["published_at"])
        print("URL:", article["url"])


if __name__ == "__main__":
    asyncio.run(main())
