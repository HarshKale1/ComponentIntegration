import axios from "axios";

const http = axios.create({
  baseURL: "http://127.0.0.1:8010",
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

function normalizeEvent(event, article = {}) {
  return {
    ...event,
    headline: event?.headline || article.title || "Financial event",
    source: event?.source || article.source || "Google News RSS",
    articleUrl: article.url || null,
    published_at: article.published_at || null,

    nodes: (event?.nodes || []).map((node, index) => ({
      ...node,
      id: node.node_id ?? node.id ?? `node-${index}`,
      label: node.label || node.name || "Unknown",
      type: node.node_type ?? node.type ?? "unknown",
      description: node.description || "",
    })),

    edges: (event?.edges || []).map((edge, index) => ({
      ...edge,
      id: edge.edge_id ?? edge.id ?? `edge-${index}`,
      source: edge.source_node_id ?? edge.source,
      target: edge.target_node_id ?? edge.target,
      relationship: edge.relationship || "related to",
      strength: edge.strength ?? 0,
      effect_direction: edge.direction ?? edge.effect_direction ?? "unknown",
      explanation: edge.explanation || "",
      evidence_type: edge.evidence_type || "unknown",
      evidence: (edge.evidence || []).map((item) => ({
        text: item.claim ?? item.text ?? "",
        source: item.source_name ?? item.source ?? "",
        url: item.url || null,
        published_at: item.published_at || null,
      })),
      historical_examples: edge.historical_examples || [],
      limitations: Array.isArray(edge.limitations)
        ? edge.limitations
        : typeof edge.limitations === "string"
          ? [edge.limitations]
          : [],
    })),
  };
}

function handleApiError(error, operation) {
  if (error.response) {
    const detail = error.response.data?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : JSON.stringify(detail || error.response.data);

    throw new Error(
      `${operation} failed (${error.response.status}): ${message}`
    );
  }

  if (error.code === "ECONNABORTED") {
    throw new Error(`${operation} timed out. Please try again.`);
  }

  if (error.code === "ERR_NETWORK") {
    throw new Error(
      `${operation} could not reach the backend at ${http.defaults.baseURL}. Check that the backend is running.`
    );
  }

  throw new Error(`${operation} failed: ${error.message}`);
}

export const api = {
  async fetchNews(query = "finance OR stock market OR economy", limit = 20) {
    try {
      const { data } = await http.get("/news", {
        params: { query, limit },
      });

      const articles = Array.isArray(data) ? data : data?.articles;

      if (!Array.isArray(articles)) {
        throw new Error("The news API did not return an articles array.");
      }

      return articles;
    } catch (error) {
      throw error instanceof Error && !error.response
        ? error
        : handleApiError(error, "Fetching news");
    }
  },

  async generateGraph(article) {
    if (!article?.title || !article?.url) {
      throw new Error("The selected article is missing its title or URL.");
    }

    try {
      const { data } = await http.post("/news/event-graph", {
        headline: article.title,
        url: article.url,
      });

      if (!data || typeof data !== "object") {
        throw new Error("The graph API returned an invalid response.");
      }

      return normalizeEvent(data, article);
    } catch (error) {
      throw error instanceof Error && !error.response
        ? error
        : handleApiError(error, "Generating event graph");
    }
  },

  async fetchMarketImpact(ticker, eventDate, windowDays = 7) {
    try {
      const { data } = await http.get("/market/event-impact", {
        params: {
          ticker: ticker.trim(),
          event_date: eventDate,
          window_days: Number(windowDays),
        },
      });

      return data;
    } catch (error) {
      throw handleApiError(error, "Fetching market impact");
    }
  },

  async health() {
    try {
      const { data } = await http.get("/health");
      return data;
    } catch (error) {
      throw handleApiError(error, "Checking backend health");
    }
  },
};
