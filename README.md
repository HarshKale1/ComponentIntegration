# 🌍 FinFlow AI — From News to Explainable Market Impact

An AI-powered financial intelligence dashboard that turns financial news and geopolitical events into an interactive market impact graph — showing how a shock may propagate across commodities, countries, sectors, indicators, and companies.

Built for the *Autonomous Financial Event Market Impact Graph* project.

---

## ✨ What It Does

1. **Live News** — pulls real, current financial headlines from Google News RSS
2. **Event Summary** — AI writes a short, factual explanation of what's happening (Gemini)
3. **Impact Graph** — AI builds a knowledge graph of nodes (commodity, country, sector, indicator) and edges (relationships with strength scores)
4. **Country Impact** — which countries are exposed, and how
5. **Sectors & Assets** — which industries and commodities are affected
6. **Key Relationships** — every edge with its strength score, evidence class, and explanation
7. **Historical Context** — real daily price data from Yahoo Finance for WTI, Brent, Gold, S&P 500, Nifty 50, Dow Jones, EUR/USD
8. **Live Stocks** — real-time quotes and 30-day charts for Indian (NSE) and US stocks
9. **AI Assistant** — a floating chat that answers market questions and can navigate the dashboard

---

## 🧱 Actual Tech Stack

| Layer | What's actually used |
|---|---|
| **Backend API** | Python, FastAPI, Uvicorn, Pydantic |
| **AI** | Google Gemini (`gemini-3.1-flash-lite` via `google-genai` SDK) |
| **Market Data** | Yahoo Finance via `yfinance` |
| **News** | Google News RSS |
| **Frontend** | Vanilla HTML / CSS / JavaScript (single-file `dashboard.html`) |
| **Charts & Graph** | Custom SVG (no chart library, no Cytoscape) |
| **Env Config** | `python-dotenv` + `.env` |
