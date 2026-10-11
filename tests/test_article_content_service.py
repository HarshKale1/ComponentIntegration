
import httpx
import pytest

from services.article_content_service import fetch_article_content


@pytest.mark.asyncio
async def test_extracts_readable_article_text(monkeypatch):
    html = """
    <html>
        <head><title>Test Article</title></head>
        <body>
            <nav>Navigation menu</nav>
            <article>
                <h1>RBI changes repo rate</h1>
                <p>The central bank announced a monetary policy decision.</p>
            </article>
            <script>ignore_this_script()</script>
        </body>
    </html>
    """

    class MockResponse:
        text = html

        def raise_for_status(self):
            pass

    class MockClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            return MockResponse()

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        MockClient,
    )

    content = await fetch_article_content("https://example.com/article")

    assert "RBI changes repo rate" in content
    assert "central bank announced" in content
    assert "Navigation menu" not in content
    assert "ignore_this_script" not in content
