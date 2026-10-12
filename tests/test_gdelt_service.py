from unittest.mock import AsyncMock, Mock

import httpx
import pytest

import services.gdelt_service as gdelt_service


@pytest.mark.asyncio
async def test_fetches_and_normalizes_articles(monkeypatch):
    payload = {
        "articles": [
            {
                "title": "  RBI changes repo rate  ",
                "url": "https://example.com/rbi",
                "domain": "example.com",
                "seendate": "20261011T100000Z",
                "language": "English",
                "sourcecountry": "India",
            }
        ]
    }

    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = payload

    client = Mock()
    client.get = AsyncMock(return_value=response)

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            assert kwargs["timeout"] == 30.0
            self.headers = kwargs["headers"]

        async def __aenter__(self):
            return client

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr(
        gdelt_service.httpx,
        "AsyncClient",
        FakeAsyncClient,
    )

    result = await gdelt_service.fetch_news(
        query="RBI repo rate",
        timespan="1d",
        max_records=5,
    )

    assert len(result) == 1
    assert result[0]["title"] == "RBI changes repo rate"
    assert result[0]["url"] == "https://example.com/rbi"
    assert result[0]["source"] == "example.com"
    assert result[0]["language"] == "English"

    client.get.assert_awaited_once()
    args, kwargs = client.get.await_args
    assert args[0] == gdelt_service.GDELT_API_URL
    assert kwargs["params"]["query"] == "RBI repo rate"
    assert kwargs["params"]["maxrecords"] == 5
    assert kwargs["params"]["sort"] == "datedesc"


@pytest.mark.asyncio
async def test_rejects_empty_query():
    with pytest.raises(ValueError, match="Query cannot be empty"):
        await gdelt_service.fetch_news(query="   ")


@pytest.mark.parametrize("limit", [0, -1, 51, 100])
@pytest.mark.asyncio
async def test_rejects_invalid_record_limit(limit):
    with pytest.raises(
        ValueError,
        match="max_records must be between 1 and 50",
    ):
        await gdelt_service.fetch_news(max_records=limit)


@pytest.mark.asyncio
async def test_wraps_http_errors(monkeypatch):
    class FakeAsyncClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            client = Mock()
            client.get = AsyncMock(
                side_effect=httpx.ConnectError("connection failed")
            )
            self.client = client
            return client

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr(
        gdelt_service.httpx,
        "AsyncClient",
        FakeAsyncClient,
    )

    with pytest.raises(
        gdelt_service.GDELTServiceError,
        match="GDELT request failed",
    ):
        await gdelt_service.fetch_news()


@pytest.mark.asyncio
async def test_rejects_invalid_json(monkeypatch):
    response = Mock()
    response.raise_for_status = Mock()
    response.json.side_effect = ValueError("invalid JSON")

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            client = Mock()
            client.get = AsyncMock(return_value=response)
            return client

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr(
        gdelt_service.httpx,
        "AsyncClient",
        FakeAsyncClient,
    )

    with pytest.raises(
        gdelt_service.GDELTServiceError,
        match="GDELT request failed",
    ):
        await gdelt_service.fetch_news()


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [None, [], "unexpected"])
async def test_rejects_unexpected_response_type(monkeypatch, payload):
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = payload

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            client = Mock()
            client.get = AsyncMock(return_value=response)
            return client

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr(
        gdelt_service.httpx,
        "AsyncClient",
        FakeAsyncClient,
    )

    with pytest.raises(
        gdelt_service.GDELTServiceError,
        match="unexpected response",
    ):
        await gdelt_service.fetch_news()


@pytest.mark.asyncio
async def test_rejects_invalid_articles_field(monkeypatch):
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = {"articles": "not a list"}

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            client = Mock()
            client.get = AsyncMock(return_value=response)
            return client

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr(
        gdelt_service.httpx,
        "AsyncClient",
        FakeAsyncClient,
    )

    with pytest.raises(
        gdelt_service.GDELTServiceError,
        match="article list has an invalid format",
    ):
        await gdelt_service.fetch_news()


@pytest.mark.asyncio
async def test_skips_malformed_articles(monkeypatch):
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = {
        "articles": [
            None,
            "not an article",
            {"title": "", "url": "https://example.com/empty"},
            {"title": "Missing URL"},
            {"title": "Invalid URL", "url": "javascript:alert(1)"},
            {"title": "Valid article", "url": "https://example.com/news"},
        ]
    }

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            client = Mock()
            client.get = AsyncMock(return_value=response)
            return client

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr(
        gdelt_service.httpx,
        "AsyncClient",
        FakeAsyncClient,
    )

    result = await gdelt_service.fetch_news()

    assert len(result) == 1
    assert result[0]["title"] == "Valid article"


@pytest.mark.asyncio
async def test_returns_empty_list_when_no_articles(monkeypatch):
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = {"articles": []}

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            client = Mock()
            client.get = AsyncMock(return_value=response)
            return client

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr(
        gdelt_service.httpx,
        "AsyncClient",
        FakeAsyncClient,
    )

    result = await gdelt_service.fetch_news()

    assert result == []
    id="y4x7qp"
