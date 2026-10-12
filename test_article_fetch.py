import asyncio
from services.article_content_service import fetch_article_content

async def main():
    url = input("Paste full Google News URL: ").strip()
    content = await fetch_article_content(url)
    print("CONTENT LENGTH:", len(content))
    print("PREVIEW:", content[:500])

asyncio.run(main())