from datetime import date, timedelta

from services.market_data_service import fetch_historical_prices


def calculate_event_impact(
    ticker: str,
    event_date: date,
    window_days: int = 7,
) -> dict:
    """
    Compare the closing price before an event with the
    closing price after the event.

    window_days counts calendar days, not trading sessions.
    """
    if not 1 <= window_days <= 30:
        raise ValueError("window_days must be between 1 and 30")

    start_date = event_date - timedelta(days=window_days + 10)
    end_date = event_date + timedelta(days=window_days + 2)

    result = fetch_historical_prices(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
    )

    prices = result["prices"]

    before = [
        item for item in prices
        if item["date"] < event_date.isoformat()
    ]
    after = [
        item for item in prices
        if item["date"] >= event_date.isoformat()
    ]

    if not before or not after:
        raise ValueError(
            "Insufficient historical prices around the event date"
        )

    baseline = before[-1]
    target_date = event_date + timedelta(days=window_days)

    # Use the latest available closing price on or before the
    # target date, so weekends and market holidays are handled.
    eligible_after = [
        item for item in after
        if item["date"] <= target_date.isoformat()
    ]

    if not eligible_after:
        raise ValueError(
            "No closing price available within the requested event window"
        )

    comparison = eligible_after[-1]

    percentage_change = (
        (comparison["close"] - baseline["close"])
        / baseline["close"]
    ) * 100

    return {
        "ticker": result["ticker"],
        "event_date": event_date.isoformat(),
        "baseline_date": baseline["date"],
        "comparison_date": comparison["date"],
        "baseline_close": baseline["close"],
        "comparison_close": comparison["close"],
        "percentage_change": round(percentage_change, 2),
        "window_days": window_days,
        "interpretation": (
            "UP" if percentage_change > 0
            else "DOWN" if percentage_change < 0
            else "UNCHANGED"
        ),
        "limitations": [
            "This is an observed price change, not proof that the event caused it.",
            "Other news and market-wide movements may affect the asset.",
            "The comparison uses the last available close before the event "
            "and the last available close on or before the target date.",
        ],
    }
