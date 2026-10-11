from datetime import date, timedelta

import yfinance as yf


def fetch_historical_prices(
    ticker: str,
    start_date: date,
    end_date: date,
) -> dict:
    """
    Fetch daily historical prices for a financial asset.

    end_date is exclusive, as in Yahoo Finance's history API.
    """
    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError("Ticker cannot be empty")

    if start_date >= end_date:
        raise ValueError("start_date must be before end_date")

    try:
        history = yf.Ticker(ticker).history(
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            interval="1d",
            auto_adjust=True,
        )
    except Exception as exc:
        raise RuntimeError("Historical market data retrieval failed") from exc

    if history.empty:
        raise ValueError(f"No historical data found for ticker: {ticker}")

    prices = []

    for timestamp, row in history.iterrows():
        close = row.get("Close")

        if close is None or not float(close) > 0:
            continue

        prices.append({
            "date": timestamp.date().isoformat(),
            "close": round(float(close), 4),
        })

    if not prices:
        raise ValueError(f"No valid closing prices found for ticker: {ticker}")

    return {
        "ticker": ticker,
        "currency": None,
        "data_points": len(prices),
        "prices": prices,
        "limitations": [
            "Historical price movements do not establish causation.",
            "Data availability and accuracy depend on the external provider.",
            "Currency is not inferred; verify the asset's trading currency separately.",
        ],
    }
