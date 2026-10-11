
import axios from "axios";

const http = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 60000,
});

function normalizeEvent(event, article = {}) {
  return {
    ...event,
    headline: event.headline || article.title || "Financial event",
    source: event.source || article.source || "Google News RSS",
    articleUrl: article.url || null,
    published_at: article.published_at || null,

    nodes: (event.nodes || []).map((node) => ({
      id: node.node_id,
      label: node.label,
      type: node.node_type,
      description: node.description || "",
    })),

    edges: (event.edges || []).map((edge) => ({
      id: edge.edge_id,
      source: edge.source_node_id,
      target: edge.target_node_id,
      relationship: edge.relationship,
      strength: edge.strength,
      effect_direction: edge.direction,
      explanation: edge.explanation,
      evidence_type: edge.evidence_type,
      evidence: (edge.evidence || []).map((item) => ({
        text: item.claim,
        source: item.source_name,
        url: item.url,
        published_at: item.published_at,
      })),
      historical_examples: [],
      limitations: edge.limitations || [],
    })),
  };
}

export const api = {
  async fetchNews(query = "finance OR stock market OR economy", limit = 20) {
    const { data } = await http.get("/news", {
      params: { query, limit },
    });

    return data.articles || [];
  },

  async generateGraph(article) {
    const { data } = await http.post("/news/event-graph", {
      headline: article.title,
      url: article.url,
    });

    return normalizeEvent(data, article);
  },

  async fetchMarketImpact(ticker, eventDate, windowDays = 7) {
    const { data } = await http.get("/market/event-impact", {
      params: {
        ticker: ticker.trim(),
        event_date: eventDate,
        window_days: Number(windowDays),
      },
    });

    return data;
  },

  async health() {
    const { data } = await http.get("/health");
    return data;
  },
};
