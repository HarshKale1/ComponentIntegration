
import asyncio

from services.news_service import fetch_news


async def main():
    articles = await fetch_news(max_records=5)

    print("Articles received:", len(articles))

    for index, article in enumerate(articles, start=1):
        print(f"\n{index}. {article['title']}")
        print("Source:", article["source"])
        print("Published:", article["published_at"])
        print("URL:", article["url"])


if __name__ == "__main__":
    asyncio.run(main())
