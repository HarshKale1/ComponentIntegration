
import { useCallback, useEffect, useState } from "react";
import { api } from "./api/client";
import GraphView from "./components/GraphView";
import EvidenceDrawer from "./components/EvidenceDrawer";
import Legend from "./components/Legend";

const DEFAULT_QUERY = "finance OR stock market OR economy";

function todayLocal() {
  const date = new Date();
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 10);
}

function publishedDate(article) {
  if (!article?.published_at) return todayLocal();

  const date = new Date(article.published_at);
  return Number.isNaN(date.getTime())
    ? todayLocal()
    : date.toISOString().slice(0, 10);
}

function Panel({ title, children, className = "" }) {
  return (
    <section
      className={`rounded-xl border border-slate-800 bg-slate-900 p-4 ${className}`}
    >
      <h2 className="mb-3 font-semibold">{title}</h2>
      {children}
    </section>
  );
}

function Metric({ label, value, detail }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950 p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-2 text-xl font-semibold">{value}</p>
      {detail && <p className="mt-1 text-xs text-slate-500">{detail}</p>}
    </div>
  );
}

export default function App() {
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [articles, setArticles] = useState([]);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [event, setEvent] = useState(null);
  const [graph, setGraph] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);

  const [loadingNews, setLoadingNews] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [loadingMarket, setLoadingMarket] = useState(false);
  const [error, setError] = useState("");
  const [marketError, setMarketError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  const [ticker, setTicker] = useState("SPY");
  const [eventDate, setEventDate] = useState(todayLocal());
  const [windowDays, setWindowDays] = useState(7);
  const [marketImpact, setMarketImpact] = useState(null);

  const loadNews = useCallback(async (searchQuery = query) => {
    setLoadingNews(true);
    setError("");

    try {
      const result = await api.fetchNews(searchQuery, 20);
      setArticles(result);
      setLastUpdated(new Date());

      if (!result.length) {
        setError("No articles found. Try a different search query.");
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Could not fetch Google News RSS. Check that FastAPI is running."
      );
    } finally {
      setLoadingNews(false);
    }
  }, [query]);

  useEffect(() => {
    loadNews(DEFAULT_QUERY);
  }, []); // Initial load only.

  const analyzeArticle = async (article) => {
    setSelectedArticle(article);
    setEvent(null);
    setGraph(null);
    setSelectedEdge(null);
    setMarketImpact(null);
    setMarketError("");
    setEventDate(publishedDate(article));
    setAnalyzing(true);
    setError("");

    try {
      const result = await api.generateGraph(article);

      // The backend returns an EventGraph validated by Pydantic.
      setEvent(result);
      setGraph({ nodes: result.nodes, edges: result.edges });
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Graph generation failed. Check the FastAPI terminal."
      );
    } finally {
      setAnalyzing(false);
    }
  };

  const analyzeMarket = async (e) => {
    e.preventDefault();
    setMarketError("");
    setMarketImpact(null);

    if (!selectedArticle || !event) {
      setMarketError("Select and analyze an article first.");
      return;
    }

    if (!ticker.trim() || !eventDate) {
      setMarketError("Enter a ticker and event date.");
      return;
    }

    setLoadingMarket(true);

    try {
      const result = await api.fetchMarketImpact(
        ticker,
        eventDate,
        windowDays
      );
      setMarketImpact(result);
    } catch (err) {
      console.error(err);
      setMarketError(
        err.response?.data?.detail ||
          err.message ||
          "Historical market analysis failed. Check the ticker and date."
      );
    } finally {
      setLoadingMarket(false);
    }
  };

  const percentage = Number(marketImpact?.percentage_change);
  const hasPercentage = Number.isFinite(percentage);
  const isPositive = percentage > 0;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="sticky top-0 z-20 flex min-h-16 flex-wrap items-center gap-4 border-b border-slate-800 bg-slate-950/95 px-5 py-3 backdrop-blur">
        <div className="min-w-44">
          <h1 className="text-lg font-bold">
            <span className="text-blue-400">↗</span> FinFlow AI
          </h1>
          <p className="text-xs text-slate-400">
            From News to Market Impact
          </p>
        </div>

        <form
          className="flex min-w-0 flex-1 gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            loadNews(query);
          }}
        >
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search financial news, companies, sectors..."
            className="min-w-0 w-full max-w-2xl rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm outline-none focus:border-blue-500"
          />
          <button
            disabled={loadingNews}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-500 disabled:opacity-50"
          >
            {loadingNews ? "Loading..." : "Search"}
          </button>
        </form>

        <div className="text-xs text-slate-400">
          {lastUpdated
            ? `RSS updated ${lastUpdated.toLocaleTimeString()}`
            : "Connecting to news"}
        </div>
      </header>

      <div className="grid min-h-[calc(100vh-4rem)] grid-cols-1 md:grid-cols-[190px_minmax(0,1fr)]">
        <aside className="border-b border-slate-800 bg-slate-950 p-3 md:border-b-0 md:border-r">
          <nav className="space-y-1 text-sm">
            {[
              ["⌂", "Dashboard"],
              ["◉", "Event Explorer"],
              ["⌘", "Impact Graph"],
              ["◷", "Historical Analysis"],
            ].map(([icon, label], index) => (
              <div
                key={label}
                className={`rounded-lg px-3 py-3 ${
                  index === 0
                    ? "border border-blue-500/50 bg-blue-500/20 text-white"
                    : "text-slate-400"
                }`}
              >
                <span className="mr-3">{icon}</span>
                {label}
              </div>
            ))}
          </nav>

          <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-3">
            <p className="font-semibold">News feed</p>
            <p className="mt-1 text-xs text-slate-400">
              {articles.length} articles loaded
            </p>
            <button
              onClick={() => loadNews(query)}
              disabled={loadingNews}
              className="mt-3 w-full rounded bg-slate-800 px-3 py-2 text-xs hover:bg-slate-700 disabled:opacity-50"
            >
              Refresh RSS
            </button>
          </div>

          <div className="mt-4">
            <Legend />
          </div>
        </aside>

        <main className="min-w-0 space-y-4 p-4 lg:p-5">
          {error && (
            <div
              role="alert"
              className="rounded-lg border border-red-800 bg-red-950/40 p-3 text-sm text-red-300"
            >
              {error}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
            <Metric label="News articles" value={articles.length} detail="Google News RSS" />
            <Metric label="Graph nodes" value={graph?.nodes.length ?? "—"} detail="Entities identified" />
            <Metric label="Relationships" value={graph?.edges.length ?? "—"} detail="Generated and schema-validated" />
            <Metric
              label="Market change"
              value={hasPercentage ? `${percentage > 0 ? "+" : ""}${percentage.toFixed(2)}%` : "—"}
              detail={marketImpact ? marketImpact.ticker : "Run historical analysis below"}
            />
          </div>

          <section className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.4fr)_minmax(280px,1fr)]">
            <Panel title="Latest financial news">
              <p className="mb-3 text-xs text-slate-500">
                Select an article to extract its event graph.
              </p>

              {loadingNews && articles.length === 0 && (
                <p className="text-sm text-slate-400">Fetching articles...</p>
              )}

              {!loadingNews && articles.length === 0 && !error && (
                <p className="text-sm text-slate-400">No articles available.</p>
              )}

              <div className="max-h-[400px] space-y-2 overflow-y-auto pr-1">
                {articles.map((article, index) => (
                  <button
                    key={`${article.url}-${index}`}
                    onClick={() => analyzeArticle(article)}
                    className={`block w-full rounded-lg border p-3 text-left transition ${
                      selectedArticle?.url === article.url
                        ? "border-blue-500 bg-blue-950/40"
                        : "border-slate-800 bg-slate-950/60 hover:border-slate-600"
                    }`}
                  >
                    <div className="mb-1 flex flex-wrap gap-2 text-xs text-slate-500">
                      <span>{article.source || "News source"}</span>
                      <span>·</span>
                      <span>{article.published_at || "Date unavailable"}</span>
                    </div>
                    <p className="text-sm font-medium leading-5">{article.title}</p>
                  </button>
                ))}
              </div>
            </Panel>

            <Panel title="Selected event">
              {selectedArticle ? (
                <>
                  <h3 className="text-base font-semibold leading-6">
                    {selectedArticle.title}
                  </h3>
                  <p className="mt-2 text-sm text-slate-400">
                    {selectedArticle.source || "Google News RSS"}
                  </p>
                  <a
                    href={selectedArticle.url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-3 inline-block text-sm text-blue-400 hover:underline"
                  >
                    Open original article ↗
                  </a>

                  <button
                    onClick={() => analyzeArticle(selectedArticle)}
                    disabled={analyzing}
                    className="mt-4 block rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-500 disabled:opacity-50"
                  >
                    {analyzing ? "Generating graph..." : "Regenerate graph"}
                  </button>

                  {event && (
                    <div className="mt-5 border-t border-slate-800 pt-4">
                      <p className="mb-2 text-xs uppercase tracking-wide text-slate-500">
                        Event summary
                      </p>
                      <p className="text-sm leading-6 text-slate-300">
                        {event.summary}
                      </p>

                      <div className="mt-3 flex flex-wrap gap-2">
                        <span className="rounded bg-slate-800 px-2 py-1 text-xs">
                          {event.event_type}
                        </span>
                        <span className="rounded bg-slate-800 px-2 py-1 text-xs">
                          Schema validated
                        </span>
                      </div>

                      {event.limitations?.length > 0 && (
                        <ul className="mt-3 list-disc space-y-1 pl-5 text-xs text-amber-300">
                          {event.limitations.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </>
              ) : (
                <p className="text-sm text-slate-500">
                  Choose a news article to start the analysis pipeline.
                </p>
              )}
            </Panel>
          </section>

          <Panel title="Event impact graph">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm text-slate-400">
                Select an edge to inspect its explanation and evidence.
              </p>
              <span className="text-xs text-slate-500">
                {graph
                  ? `${graph.nodes.length} nodes · ${graph.edges.length} relationships`
                  : "Awaiting graph"}
              </span>
            </div>

            <div className="h-[500px]">
              {analyzing ? (
                <div className="flex h-full items-center justify-center text-sm text-slate-400">
                  Extracting article content and generating graph...
                </div>
              ) : graph ? (
                <GraphView graph={graph} onEdgeClick={setSelectedEdge} />
              ) : (
                <div className="flex h-full items-center justify-center rounded-lg border border-dashed border-slate-800 p-8 text-center text-sm text-slate-500">
                  Select a news article above to generate its graph.
                </div>
              )}
            </div>
          </Panel>

          <Panel title="Historical market analysis">
            <p className="mb-4 text-sm leading-6 text-slate-400">
              Compare historical closing prices before and after the selected
              event date. This measures observed movement, not proof of causation.
            </p>

            <form
              onSubmit={analyzeMarket}
              className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4"
            >
              <label className="text-xs text-slate-400">
                Market ticker
                <input
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value)}
                  placeholder="e.g. SPY, AAPL, RELIANCE.NS"
                  className="mt-1 block w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-blue-500"
                  required
                />
              </label>

              <label className="text-xs text-slate-400">
                Event date
                <input
                  type="date"
                  value={eventDate}
                  onChange={(e) => setEventDate(e.target.value)}
                  max={todayLocal()}
                  className="mt-1 block w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-blue-500"
                  required
                />
              </label>

              <label className="text-xs text-slate-400">
                Comparison window
                <select
                  value={windowDays}
                  onChange={(e) => setWindowDays(Number(e.target.value))}
                  className="mt-1 block w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-blue-500"
                >
                  {[1, 3, 7, 14, 30].map((days) => (
                    <option key={days} value={days}>
                      {days} calendar days
                    </option>
                  ))}
                </select>
              </label>

              <div className="flex items-end">
                <button
                  type="submit"
                  disabled={loadingMarket || analyzing || !event}
                  className="w-full rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loadingMarket ? "Analyzing..." : "Analyze price impact"}
                </button>
              </div>
            </form>

            {!event && (
              <p className="mt-3 text-xs text-amber-300">
                Generate an event graph first to enable this analysis.
              </p>
            )}

            {marketError && (
              <p role="alert" className="mt-4 rounded-lg border border-red-800 bg-red-950/40 p-3 text-sm text-red-300">
                {marketError}
              </p>
            )}

            {marketImpact && (
              <div className="mt-5 space-y-4">
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                  <Metric
                    label="Observed price change"
                    value={`${percentage > 0 ? "+" : ""}${percentage.toFixed(2)}%`}
                    detail={marketImpact.interpretation}
                  />
                  <Metric
                    label="Baseline close"
                    value={marketImpact.baseline_close}
                    detail={marketImpact.baseline_date}
                  />
                  <Metric
                    label="Comparison close"
                    value={marketImpact.comparison_close}
                    detail={marketImpact.comparison_date}
                  />
                </div>

                <div className={`rounded-lg border p-4 ${
                  isPositive
                    ? "border-emerald-800 bg-emerald-950/20"
                    : percentage < 0
                      ? "border-red-800 bg-red-950/20"
                      : "border-slate-700 bg-slate-950"
                }`}>
                  <p className="font-semibold">
                    {marketImpact.ticker}:{" "}
                    {marketImpact.interpretation}
                  </p>
                  <p className="mt-1 text-sm text-slate-300">
                    Closing-price comparison from {marketImpact.baseline_date}
                    {" "}to {marketImpact.comparison_date}, around the event date
                    {" "}{marketImpact.event_date}.
                  </p>
                </div>

                {marketImpact.limitations?.length > 0 && (
                  <ul className="list-disc space-y-1 pl-5 text-xs text-amber-300">
                    {marketImpact.limitations.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </Panel>

          <p className="text-xs leading-5 text-slate-500">
            Graphs are schema-validated, but generated relationships are not
            automatically verified facts. Historical price movements do not
            establish that an event caused them. Market analysis requires a
            supported ticker and available historical price data.
          </p>
        </main>
      </div>

      {selectedEdge && (
        <EvidenceDrawer
          edge={selectedEdge}
          onClose={() => setSelectedEdge(null)}
        />
      )}
    </div>
  );
}
