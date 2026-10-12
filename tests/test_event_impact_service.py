from datetime import date, timedelta
from unittest.mock import Mock

import pytest

import services.event_impact_service as impact_service


EVENT_DATE = date(2026, 10, 12)


@pytest.fixture
def mock_prices(monkeypatch):
    fetch = Mock()
    monkeypatch.setattr(
        impact_service,
        "fetch_historical_prices",
        fetch,
    )
    return fetch


def price(day, close):
    return {"date": day.isoformat(), "close": close}


def test_calculates_positive_price_change(mock_prices):
    mock_prices.return_value = {
        "ticker": "TEST",
        "prices": [
            price(EVENT_DATE - timedelta(days=1), 100.0),
            price(EVENT_DATE, 105.0),
            price(EVENT_DATE + timedelta(days=3), 110.0),
            price(EVENT_DATE + timedelta(days=7), 112.0),
        ],
    }

    result = impact_service.calculate_event_impact(
        ticker="TEST",
        event_date=EVENT_DATE,
        window_days=7,
    )

    assert result["baseline_close"] == 100.0
    assert result["comparison_close"] == 112.0
    assert result["percentage_change"] == 12.0
    assert result["interpretation"] == "UP"
    assert result["window_days"] == 7
    assert len(result["limitations"]) > 0


def test_calculates_negative_price_change(mock_prices):
    mock_prices.return_value = {
        "ticker": "TEST",
        "prices": [
            price(EVENT_DATE - timedelta(days=1), 100.0),
            price(EVENT_DATE, 90.0),
            price(EVENT_DATE + timedelta(days=7), 80.0),
        ],
    }

    result = impact_service.calculate_event_impact(
        ticker="TEST",
        event_date=EVENT_DATE,
        window_days=7,
    )

    assert result["percentage_change"] == -20.0
    assert result["interpretation"] == "DOWN"


def test_detects_unchanged_price(mock_prices):
    mock_prices.return_value = {
        "ticker": "TEST",
        "prices": [
            price(EVENT_DATE - timedelta(days=1), 100.0),
            price(EVENT_DATE, 100.0),
            price(EVENT_DATE + timedelta(days=7), 100.0),
        ],
    }

    result = impact_service.calculate_event_impact(
        ticker="TEST",
        event_date=EVENT_DATE,
        window_days=7,
    )

    assert result["percentage_change"] == 0.0
    assert result["interpretation"] == "UNCHANGED"


@pytest.mark.parametrize("window_days", [0, -1, 31, 100])
def test_rejects_invalid_window(mock_prices, window_days):
    with pytest.raises(
        ValueError,
        match="window_days must be between 1 and 30",
    ):
        impact_service.calculate_event_impact(
            ticker="TEST",
            event_date=EVENT_DATE,
            window_days=window_days,
        )

    mock_prices.assert_not_called()


def test_rejects_missing_prices_before_event(mock_prices):
    mock_prices.return_value = {
        "ticker": "TEST",
        "prices": [
            price(EVENT_DATE, 100.0),
            price(EVENT_DATE + timedelta(days=7), 110.0),
        ],
    }

    with pytest.raises(
        ValueError,
        match="Insufficient historical prices",
    ):
        impact_service.calculate_event_impact(
            ticker="TEST",
            event_date=EVENT_DATE,
            window_days=7,
        )


def test_rejects_missing_prices_after_event(mock_prices):
    mock_prices.return_value = {
        "ticker": "TEST",
        "prices": [
            price(EVENT_DATE - timedelta(days=1), 100.0),
        ],
    }

    with pytest.raises(
        ValueError,
        match="Insufficient historical prices",
    ):
        impact_service.calculate_event_impact(
            ticker="TEST",
            event_date=EVENT_DATE,
            window_days=7,
        )


def test_rejects_prices_only_beyond_requested_window(mock_prices):
    mock_prices.return_value = {
        "ticker": "TEST",
        "prices": [
            price(EVENT_DATE - timedelta(days=1), 100.0),
            price(EVENT_DATE + timedelta(days=10), 110.0),
        ],
    }

    with pytest.raises(
        ValueError,
        match="No closing price available",
    ):
        impact_service.calculate_event_impact(
            ticker="TEST",
            event_date=EVENT_DATE,
            window_days=7,
        )


def test_uses_last_available_close_on_or_before_target_date(mock_prices):
    mock_prices.return_value = {
        "ticker": "TEST",
        "prices": [
            price(EVENT_DATE - timedelta(days=1), 100.0),
            price(EVENT_DATE, 101.0),
            price(EVENT_DATE + timedelta(days=3), 105.0),
            price(EVENT_DATE + timedelta(days=6), 108.0),
            price(EVENT_DATE + timedelta(days=8), 120.0),
        ],
    }

    result = impact_service.calculate_event_impact(
        ticker="TEST",
        event_date=EVENT_DATE,
        window_days=7,
    )

    assert result["comparison_date"] == (
        EVENT_DATE + timedelta(days=6)
    ).isoformat()
    assert result["comparison_close"] == 108.0
    assert result["percentage_change"] == 8.0


def test_passes_expected_date_range_to_market_service(mock_prices):
    mock_prices.return_value = {
        "ticker": "TEST",
        "prices": [
            price(EVENT_DATE - timedelta(days=1), 100.0),
            price(EVENT_DATE, 105.0),
        ],
    }

    impact_service.calculate_event_impact(
        ticker="TEST",
        event_date=EVENT_DATE,
        window_days=7,
    )

    mock_prices.assert_called_once_with(
        ticker="TEST",
        start_date=EVENT_DATE - timedelta(days=17),
        end_date=EVENT_DATE + timedelta(days=9),
    )
    id="u1d6c5"
