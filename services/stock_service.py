"""
Stock market data service using Yahoo Finance (yfinance).

Provides:
- fetch_quotes: current price, change, and 30-day sparkline data for multiple symbols
- fetch_candles: historical OHLC for a single symbol over N days
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import yfinance as yf


# Friendly names for common tickers (used in the UI)
DISPLAY_NAMES = {
    # Indian (NSE)
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys",
    "ICICIBANK.NS": "ICICI Bank",
    # US
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "TSLA": "Tesla",
    "NVDA": "Nvidia",
    # Indices
    "^NSEI": "Nifty 50",
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones",
}

# Regions for grouping in the UI
REGIONS = {
    "RELIANCE.NS": "IN", "TCS.NS": "IN", "HDFCBANK.NS": "IN",
    "INFY.NS": "IN", "ICICIBANK.NS": "IN",
    "AAPL": "US", "MSFT": "US", "GOOGL": "US", "TSLA": "US", "NVDA": "US",
    "^NSEI": "INDEX", "^GSPC": "INDEX", "^DJI": "INDEX",
}


def _safe_float(v: Any) -> float | None:
    try:
        if v is None:
            return None
        f = float(v)
        if f != f:  # NaN check
            return None
        return round(f, 2)
    except (TypeError, ValueError):
        return None


def fetch_quotes(symbols: list[str]) -> list[dict]:
    """
    Fetch current quotes + a 30-day sparkline for each symbol.

    Returns a list of dicts with:
      symbol, name, region, price, change, change_pct,
      currency, volume, sparkline (list of floats)
    """
    out: list[dict] = []
    for sym in symbols:
        sym = sym.strip()
        if not sym:
            continue
        try:
            t = yf.Ticker(sym)
            # 1-month history for sparkline
            hist = t.history(period="1mo", interval="1d", auto_adjust=False)
            info = {}
            try:
                info = t.fast_info or {}
            except Exception:
                pass

            price = None
            prev_close = None
            currency = "USD"
            volume = None

            if hist is not None and not hist.empty:
                price = _safe_float(hist["Close"].iloc[-1])
                if len(hist) >= 2:
                    prev_close = _safe_float(hist["Close"].iloc[-2])
                try:
                    volume = int(hist["Volume"].iloc[-1])
                except Exception:
                    volume = None
                sparkline = [round(float(x), 2) for x in hist["Close"].dropna().tolist()][-30:]
                currency = "INR" if (sym.endswith(".NS") or sym.startswith("^NSE") or sym.startswith("^BSE")) else "USD"
            else:
                sparkline = []

            # Try fast_info if history failed
            if price is None:
                try:
                    price = _safe_float(info.get("last_price"))
                except Exception:
                    pass
            if prev_close is None:
                try:
                    prev_close = _safe_float(info.get("previous_close"))
                except Exception:
                    pass

            change = None
            change_pct = None
            if price is not None and prev_close is not None and prev_close != 0:
                change = round(price - prev_close, 2)
                change_pct = round((price - prev_close) / prev_close * 100, 2)

            out.append({
                "symbol": sym,
                "name": DISPLAY_NAMES.get(sym, sym),
                "region": REGIONS.get(sym, "OTHER"),
                "price": price,
                "change": change,
                "change_pct": change_pct,
                "currency": currency,
                "volume": volume,
                "sparkline": sparkline,
            })
        except Exception as exc:
            out.append({
                "symbol": sym,
                "name": DISPLAY_NAMES.get(sym, sym),
                "region": REGIONS.get(sym, "OTHER"),
                "error": str(exc),
                "price": None, "change": None, "change_pct": None,
                "currency": None, "volume": None, "sparkline": [],
            })
    return out


def fetch_candles(symbol: str, days: int = 30) -> dict:
    """
    Fetch OHLC historical data for a single symbol.
    Returns { symbol, name, region, currency, candles: [{date, open, high, low, close, volume}] }
    """
    symbol = symbol.strip()
    if not symbol:
        raise ValueError("symbol is required")

    days = max(5, min(days, 365))
    t = yf.Ticker(symbol)

    # yfinance period strings: 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y
    if days <= 7:
        period = "5d"
    elif days <= 35:
        period = "1mo"
    elif days <= 100:
        period = "3mo"
    elif days <= 200:
        period = "6mo"
    else:
        period = "1y"

    hist = t.history(period=period, interval="1d", auto_adjust=False)

    candles = []
    if hist is not None and not hist.empty:
        for idx, row in hist.iterrows():
            try:
                candles.append({
                    "date": idx.strftime("%Y-%m-%d"),
                    "open": _safe_float(row["Open"]),
                    "high": _safe_float(row["High"]),
                    "low": _safe_float(row["Low"]),
                    "close": _safe_float(row["Close"]),
                    "volume": int(row["Volume"]) if row["Volume"] == row["Volume"] else None,
                })
            except Exception:
                continue

    currency = "INR" if (symbol.endswith(".NS") or symbol.startswith("^NSE") or symbol.startswith("^BSE")) else "USD"

    return {
        "symbol": symbol,
        "name": DISPLAY_NAMES.get(symbol, symbol),
        "region": REGIONS.get(symbol, "OTHER"),
        "currency": currency,
        "candles": candles,
    }