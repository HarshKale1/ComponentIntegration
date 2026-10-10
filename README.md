# 🌍 Autonomous Financial Event Market Impact Graph

### 📊 From Financial News to Explainable Market Impact

An AI-powered financial intelligence system that analyzes financial news and geopolitical events to understand how they may affect countries, commodities, industries, companies, and financial markets.

Instead of simply predicting stock prices, this project focuses on explaining **what happened, how its effects may spread, and what evidence supports each relationship.**

---

## 🎯 About the Project

Financial events rarely affect just one market or company. A geopolitical conflict, oil supply disruption, or major economic announcement can influence several connected parts of the global economy.

For example, an increase in crude oil prices may raise transportation costs, contribute to inflationary pressure, and affect countries differently depending on their energy requirements.

The **Autonomous Financial Event Market Impact Graph** aims to make these connections easier to understand through an interactive knowledge graph backed by AI-based information extraction, evidence analysis, and historical market data.

Our goal is to build a system that explains the possible chain of financial impacts rather than simply generating predictions.

## ❓ The Problem

Understanding the impact of financial news requires connecting information from different sources and identifying relationships between economic events, countries, commodities, sectors, and financial assets.

Traditional news summaries explain what happened, while stock prediction tools mainly focus on potential price movements. They may not explain the complete chain of economic relationships behind an event.

This project aims to connect these relationships in one place and make the reasoning, supporting evidence, and uncertainty visible.

## 💡 Our Approach

The system will transform a financial event into an interactive graph of connected entities and possible impact pathways.

The planned workflow includes:

1. 📰 **Event Extraction:** Analyze news articles or manually entered events.
2. 🧠 **Entity Identification:** Identify relevant countries, companies, commodities, sectors, and economic indicators.
3. 🔗 **Knowledge Graph Construction:** Connect entities through directed economic relationships.
4. 📈 **Relationship Scoring:** Assign numerical strength scores using a documented methodology.
5. 🛤️ **Impact Path Analysis:** Trace possible effects from the original event to related sectors and financial assets.
6. 📚 **Historical Analysis:** Compare proposed relationships with verified historical events and market data.
7. 🔍 **Evidence Exploration:** Allow users to inspect sources, explanations, limitations, and uncertainty.

## 🛢️ Example: Oil Supply Disruption

Imagine a geopolitical event disrupts crude oil supplies.

Possible impact pathways include:

**🚚 Transportation**

Oil supply disruption → Crude oil prices rise → Fuel costs may increase → Transportation operating costs may rise → Airline and logistics company margins may come under pressure.

**📉 Inflation and Monetary Policy**

Crude oil prices rise → Energy costs may increase → Inflationary pressure may rise → Interest-rate expectations may change → Banks and real estate companies may be affected.

**🌐 Country-Wise Economic Impact**

Oil supply disruption → Changes in oil availability and prices → Different consequences for oil-importing and oil-producing countries.

These pathways are hypotheses, not guaranteed outcomes. The system will aim to investigate supporting evidence and explain the factors that may strengthen or weaken each relationship.

## ✨ Key Features

- 📰 **Financial Event Analysis** — Extract structured information from financial news and geopolitical events.
- 🧠 **AI-Based Information Extraction** — Identify entities, event details, quantitative claims, and candidate relationships.
- 🕸️ **Interactive Knowledge Graph** — Explore connections between events, countries, commodities, indicators, sectors, companies, and assets.
- 🎚️ **Relationship Strength Scoring** — Assign each relationship a documented score between 0 and 1.
- 🔎 **Evidence Explorer** — Inspect relationship explanations, supporting sources, historical examples, and limitations.
- 🛤️ **Impact Path Analysis** — Identify and rank possible routes through which an event may affect financial assets.
- 🗺️ **Country-Wise Impact Analysis** — Compare economic exposure across countries and regions.
- 📊 **Historical Market Analysis** — Examine relevant price movements and event-window returns using verified data.
- ⚖️ **Uncertainty Handling** — Distinguish observed facts, established economic relationships, and inferred hypotheses.

*These are planned capabilities and should be considered complete only after implementation and testing.*

## 🎚️ Relationship Strength

Every graph relationship will have a numerical strength score between `0` and `1`.

| Score | Strength | Color |
|---|---|---|
| 0.70–1.00 | Strong | 🔴 Red |
| 0.40–0.69 | Medium | 🟠 Amber |
| 0.00–0.39 | Weak | 🟢 Green |

The scoring methodology will consider factors such as economic dependency, historical support, evidence quality, source reliability, recency, independent-source agreement, and contradictory evidence.

**Important:** Relationship strength is not the same as impact severity or the probability of a future market movement. A score of 0.82 does not automatically mean an 82% chance of a stock price declining.

## 🔍 Evidence and Explainability

The project aims to make every important graph relationship understandable and verifiable.

When a user selects a relationship, the planned evidence panel will show:

- Source and target entities.
- Relationship type and direction.
- Numerical strength score.
- Explanation of the economic mechanism.
- Supporting evidence and source links.
- Publication and event dates.
- Historical examples, where verified data is available.
- Alternative explanations and limitations.
- Classification of the relationship.

The system will distinguish between:

- ✅ **Observed Facts:** Claims supported by sources or recorded data.
- 📖 **Established Relationships:** Economic mechanisms supported by credible evidence.
- 💭 **Inferred Hypotheses:** Possible connections that require further verification.

If reliable evidence is unavailable, the application should display **"Insufficient verified evidence"** instead of inventing statistics, historical events, or citations.

## 🌐 Country-Wise Impact Analysis

The planned global map will help users explore how the same event may affect different economies.

Depending on the event and available data, the system may examine:

- Commodity production and import dependency.
- Energy supply and alternative suppliers.
- Export exposure and trade relationships.
- Inflation and domestic energy costs.
- Currency and trade-balance exposure.
- Affected industries and financial assets.
- Short-term and long-term economic transmission channels.
- Historical evidence and uncertainty.

Users will be able to select a country and explore its relevant sectors, assets, impact pathways, and supporting evidence.

Rather than assigning an unexplained overall impact score, the system will show separate exposure dimensions and explain how they are calculated.

## 📈 Historical Market Analysis

Historical data will help evaluate whether proposed relationships are consistent with past observations.

Where reliable data is available, the system will examine:

- Verified event dates and original sources.
- Relevant commodity price movements.
- Sector and asset returns before and after an event.
- The selected event window.
- Country and industry exposure.
- Possible confounding factors.
- Whether the evidence supports, contradicts, or is insufficient to assess a proposed relationship.

Historical correlation alone does not prove causation. The system will distinguish observed market movements from interpretations about their causes.

## 🛠️ Proposed Technology Stack

The initial implementation will use a modular monolith to keep development and integration manageable.

| Component | Technology |
|---|---|
| Frontend | React and Vite |
| Interactive Graph | Cytoscape.js |
| Backend API | Python and FastAPI |
| Data Validation | Pydantic |
| Knowledge Graph | Neo4j and Cypher |
| Data Analysis | pandas and NumPy |
| AI and NLP | LLM API with structured outputs |
| Charts | React-compatible charting library |
| Country Map | Leaflet or MapLibre GL |
| Version Control | Git and GitHub |

The exact dependencies and versions will be finalized during implementation. Historical market data will come from a suitable provider or verified prepared datasets, subject to availability and licensing.

## 🗺️ MVP Development Roadmap

The first version will focus on one complete workflow instead of implementing every advanced feature simultaneously.

- [ ] **Phase 1:** Define shared JSON schemas and relationship vocabulary.
- [ ] **Phase 2:** Create a small, manually reviewed knowledge graph.
- [ ] **Phase 3:** Build the React graph interface using mock data.
- [ ] **Phase 4:** Implement the FastAPI event extraction endpoint.
- [ ] **Phase 5:** Connect Neo4j and implement graph queries.
- [ ] **Phase 6:** Add relationship scoring and impact path traversal.
- [ ] **Phase 7:** Build the clickable evidence panel.
- [ ] **Phase 8:** Add verified historical examples and market charts.
- [ ] **Phase 9:** Develop country-wise analysis and the global map.
- [ ] **Phase 10:** Test the complete workflow and document limitations.

The roadmap checkboxes will be updated as features are implemented and tested.

## 👥 Team Responsibilities

The initial MVP is divided between two members.

### 🧠 Member 1 — Backend, AI, and Knowledge Graph

- Set up the Python and FastAPI project.
- Implement event and entity extraction.
- Define and validate shared data schemas.
- Store and retrieve entities and relationships using Neo4j.
- Develop the relationship-scoring methodology.
- Implement impact-path traversal and ranking.
- Connect evidence and historical references to relationships.
- Return structured JSON responses to the frontend.

**Deliverable:** A backend that accepts an event and returns validated entities, scored relationships, impact paths, and available supporting evidence.

### 🎨 Member 2 — Frontend, Visualization, and Integration

- Build the React dashboard and event input.
- Render the interactive graph using Cytoscape.js.
- Implement relationship-strength styling and graph interactions.
- Build the impact-path and evidence panels.
- Develop the country map and comparison interface.
- Add historical charts when validated data is available.
- Integrate the frontend with the backend.
- Test the complete user workflow.

**Deliverable:** An interactive dashboard where users can submit an event, explore its graph, inspect relationships, and compare possible impacts.

Both members should agree on the shared API contract early. The frontend can use mock data while the backend is being developed.

## 🧪 Evaluation and Testing

The project will not claim a fixed accuracy percentage before evaluation.

Testing will use a manually reviewed set of events and assess:

- Entity extraction precision and recall.
- Relationship extraction precision and recall.
- Evidence validity and traceability.
- Relevance of generated impact paths.
- Correctness of country and asset mappings.
- Accuracy of historical data and calculations.
- Predictive performance, if a separate prediction model is developed.

Any future prediction model will be evaluated separately from the extraction and graph components, with safeguards against data leakage.

## 🚀 Future Scope
Once the core MVP is working, possible improvements include:

- 📡 Live financial news monitoring.
- 🔄 Automatic knowledge graph updates.
- 🔔 Alerts when new evidence changes a relationship.
- 🔀 Alternative scenario analysis.
- ⏳ Short-term and long-term impact views.
- ⚖️ Contradictory-signal analysis.
- ⭐ Country, sector, and asset watchlists.
- 🗂️ Historical analogue search.
- 📏 Improved score calibration and formal evaluation.
- 📄 Exportable impact reports.

### 🌍 Autonomous Financial Event Market Impact Graph

**Trace the shock. Test the chain. Check reality.**
