from datetime import date
from unittest.mock import Mock

import pandas as pd
import pytest

import services.market_data_service as market_service


START_DATE = date(2026, 10, 1)
END_DATE = date(2026, 10, 5)


def sample_history():
    return pd.DataFrame(
        {"Close": [100.123456, 105.0, 110.0]},
        index=pd.to_datetime([
            "2026-10-01",
            "2026-10-02",
            "2026-10-03",
        ]),
    )


def test_fetches_and_formats_historical_prices(monkeypatch):
    ticker_mock = Mock()
    ticker_mock.history.return_value = sample_history()
    monkeypatch.setattr(
        market_service.yf,
        "Ticker",
        Mock(return_value=ticker_mock),
    )

    result = market_service.fetch_historical_prices(
        " test ",
        START_DATE,
        END_DATE,
    )

    assert result["ticker"] == "TEST"
    assert result["currency"] is None
    assert result["data_points"] == 3
    assert result["prices"][0] == {
        "date": "2026-10-01",
        "close": 100.1235,
    }
    assert result["prices"][-1]["close"] == 110.0
    assert result["limitations"]

    ticker_mock.history.assert_called_once_with(
        start="2026-10-01",
        end="2026-10-05",
        interval="1d",
        auto_adjust=True,
    )


def test_rejects_empty_ticker(monkeypatch):
    ticker_mock = Mock()
    monkeypatch.setattr(
        market_service.yf,
        "Ticker",
        Mock(return_value=ticker_mock),
    )

    with pytest.raises(ValueError, match="Ticker cannot be empty"):
        market_service.fetch_historical_prices(
            "   ",
            START_DATE,
            END_DATE,
        )

    ticker_mock.history.assert_not_called()


def test_rejects_invalid_date_range(monkeypatch):
    ticker_mock = Mock()
    monkeypatch.setattr(
        market_service.yf,
        "Ticker",
        Mock(return_value=ticker_mock),
    )

    with pytest.raises(ValueError, match="start_date must be before end_date"):
        market_service.fetch_historical_prices(
            "TEST",
            END_DATE,
            START_DATE,
        )

    ticker_mock.history.assert_not_called()


def test_wraps_provider_exception(monkeypatch):
    ticker_mock = Mock()
    ticker_mock.history.side_effect = Exception("provider failure")
    monkeypatch.setattr(
        market_service.yf,
        "Ticker",
        Mock(return_value=ticker_mock),
    )

    with pytest.raises(
        RuntimeError,
        match="Historical market data retrieval failed",
    ):
        market_service.fetch_historical_prices(
            "TEST",
            START_DATE,
            END_DATE,
        )


def test_rejects_empty_history(monkeypatch):
    ticker_mock = Mock()
    ticker_mock.history.return_value = pd.DataFrame()
    monkeypatch.setattr(
        market_service.yf,
        "Ticker",
        Mock(return_value=ticker_mock),
    )

    with pytest.raises(ValueError, match="No historical data found"):
        market_service.fetch_historical_prices(
            "TEST",
            START_DATE,
            END_DATE,
        )


def test_rejects_history_with_no_valid_closing_prices(monkeypatch):
    ticker_mock = Mock()
    ticker_mock.history.return_value = pd.DataFrame(
        {"Close": [None, 0.0, -5.0]},
        index=pd.to_datetime([
            "2026-10-01",
            "2026-10-02",
            "2026-10-03",
        ]),
    )
    monkeypatch.setattr(
        market_service.yf,
        "Ticker",
        Mock(return_value=ticker_mock),
    )

    with pytest.raises(
        ValueError,
        match="No valid closing prices found",
    ):
        market_service.fetch_historical_prices(
            "TEST",
            START_DATE,
            END_DATE,
        )


def test_skips_missing_and_nonpositive_closes(monkeypatch):
    ticker_mock = Mock()
    ticker_mock.history.return_value = pd.DataFrame(
        {"Close": [100.0, None, 0.0, -1.0, 120.0]},
        index=pd.to_datetime([
            "2026-10-01",
            "2026-10-02",
            "2026-10-03",
            "2026-10-04",
            "2026-10-05",
        ]),
    )
    monkeypatch.setattr(
        market_service.yf,
        "Ticker",
        Mock(return_value=ticker_mock),
    )

    result = market_service.fetch_historical_prices(
        "TEST",
        START_DATE,
        END_DATE,
    )

    assert result["data_points"] == 2
    assert [item["close"] for item in result["prices"]] == [
        100.0,
        120.0,
    ]


def test_normalizes_ticker_before_request(monkeypatch):
    ticker_factory = Mock()
    ticker_mock = Mock()
    ticker_mock.history.return_value = sample_history()
    ticker_factory.return_value = ticker_mock
    monkeypatch.setattr(
        market_service.yf,
        "Ticker",
        ticker_factory,
    )

    market_service.fetch_historical_prices(
        "  aapl ",
        START_DATE,
        END_DATE,
    )

    ticker_factory.assert_called_once_with("AAPL")


def test_preserves_provider_price_order(monkeypatch):
    ticker_mock = Mock()
    ticker_mock.history.return_value = pd.DataFrame(
        {"Close": [110.0, 100.0]},
        index=pd.to_datetime([
            "2026-10-03",
            "2026-10-01",
        ]),
    )
    monkeypatch.setattr(
        market_service.yf,
        "Ticker",
        Mock(return_value=ticker_mock),
    )

    result = market_service.fetch_historical_prices(
        "TEST",
        START_DATE,
        END_DATE,
    )

    assert [item["date"] for item in result["prices"]] == [
        "2026-10-03",
        "2026-10-01",
    ]
    id="7zmx8a"
