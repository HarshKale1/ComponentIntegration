# Autonomous-Financial-Event-Market-Impact-Graph

> Tagline: Trace the shock. Test the chain. Check reality.

## Overview

The Autonomous Financial Event Market Impact Graph is an AI-powered system that analyzes financial news and shows how an event could affect industries, companies, and financial assets through connected relationships.

Instead of only summarizing a news article, the system extracts important events and entities, builds an interactive impact graph, traces possible ripple effects, and compares those hypotheses with historical market behaviour. It also shows the evidence and uncertainty behind each relationship so users can understand why a possible impact is suggested.

The initial focus is on the Indian financial market, with selected sectors and assets used to demonstrate how one event can affect several connected parts of the economy.

## Problem Statement

Financial events rarely affect only one company or sector. For example, a rise in crude oil prices may affect oil-marketing companies, aviation costs, inflation expectations, the Indian rupee, and interest-rate expectations.

These relationships are difficult to follow when information is spread across news articles, market data, and sector reports. A simple news summary does not show the full chain of possible effects, while a graph without evidence can make uncertain relationships look like facts.

## Our Solution

The system converts financial information into an evidence-backed, interactive graph of possible market impacts.

It is designed to help users:

- Identify the main event described in financial news.
- Extract relevant companies, sectors, commodities, currencies, and economic indicators.
- View direct and multi-step relationships between those entities.
- Explore possible positive, negative, or uncertain effects.
- Inspect the evidence behind a relationship.
- Compare an expected impact with observed historical market movements.
- Test alternative assumptions and explore how the impact path may change.

The system supports analysis and decision-making. It does not guarantee future market movements or treat correlation as proof of causation.

## Key Features

### 1. Financial Event Detection
Analyze a news article or supplied financial text to identify the main event, its context, and the entities involved.

### 2. Entity and Relationship Extraction
Extract relevant entities such as companies, industries, commodities, currencies, and economic indicators, then identify potential relationships between them.

### 3. Interactive Impact Graph
Display entities as nodes and relationships as connected edges. Users can explore direct effects and follow possible multi-step impact paths.

### 4. Evidence-Backed Relationships
Attach supporting information or an explanation to graph relationships. Where evidence is weak, incomplete, or conflicting, the system should communicate that uncertainty instead of presenting an inference as a confirmed fact.

### 5. Multi-Step Impact Tracing
Trace how an event might spread across connected sectors and assets. For example, a commodity-price change could affect company costs, sector performance, inflation expectations, and currency or interest-rate expectations.

### 6. Expected Impact vs. Market Reality
Compare a proposed impact path with available historical market data. This helps users see whether observed price movements were consistent with the hypothesis, while accounting for the fact that many other factors can move markets.

### 7. Historical Event Analysis
Use selected past events to examine how related assets behaved over a defined time window. Results should be treated as historical evidence, not a guarantee of future outcomes.

### 8. Scenario and Counterfactual Exploration
Allow users to change an assumption or explore an alternative scenario and see how the proposed impact path changes. The system should clearly label scenario results as hypothetical.

### 9. Confidence and Uncertainty
Show confidence or evidence strength for extracted relationships where supported by the method. Confidence scores are not the same as the probability that a market prediction will come true.

## What Makes This Project Different?

A basic financial-news tool may summarize an article or draw a graph of connected companies. Our approach aims to go further by combining:

- Impact propagation: tracing possible effects across multiple connected entities.
- Evidence at each connection: showing why a relationship is included.
- Reality checking: comparing the proposed impact with observed historical market behaviour.
- Scenario exploration: testing how different assumptions may change the path.
- Transparent uncertainty: distinguishing reported facts, inferred relationships, and hypothetical outcomes.

The goal is not to claim that every market move can be predicted. The goal is to make financial impact reasoning easier to inspect, test, and understand.

## Example Use Case

Input event: Crude oil prices rise sharply.

The system may build a possible impact chain such as:

1. Crude oil prices rise.
2. Fuel and input costs may increase for selected businesses.
3. Aviation companies may face higher operating costs.
4. Oil-marketing companies may experience different effects depending on pricing policy, margins, and other conditions.
5. Inflation expectations and currency movements may also be affected by broader market conditions.

The graph should show the supporting evidence, the direction of each proposed relationship where it can be justified, and any uncertainty. It can then compare selected assets with historical market data over a defined period.

This is an illustrative scenario, not a claim that every listed outcome must occur.

## Initial Scope

The first version is intended to focus on a manageable set of Indian-market relationships, such as:

- Crude oil and related companies
- Aviation
- Oil-marketing companies
- The Indian rupee
- Inflation and interest-rate expectations
- Selected banking, paints, and real-estate connections

The exact coverage depends on the availability and reliability of news, entity, and market data.

## How It Works

1. Input: The user supplies a financial news article or event description.
2. Analyze: An AI extraction layer identifies the event, entities, and candidate relationships.
3. Validate: Structured-output checks and rules help standardize and validate the extracted information.
4. Build graph: The system represents entities as nodes and relationships as edges, retaining evidence and uncertainty information.
5. Trace impact: A graph-analysis component explores possible direct and multi-step paths.
6. Check market data: Available historical price data is examined over a specified window and compared with the proposed impact.
7. Explore scenarios: The user can adjust assumptions and inspect alternative paths.
8. Present results: A dashboard displays the graph, explanations, evidence, historical comparisons, and limitations.

## Proposed Technology Stack

| Component | Proposed Technology |
| --- | --- |
| Frontend | React + TypeScript |
| Graph visualization | Cytoscape.js or React Flow |
| Backend API | Python + FastAPI |
| AI extraction | LLM with structured JSON output |
| Data validation | Pydantic and custom validation rules |
| Graph analysis | NetworkX |
| Graph database (optional) | Neo4j |
| Historical market data | A suitable market-data provider, such as yfinance where appropriate |
| Charts | Recharts or Plotly |
| Initial storage | SQLite; expandable as needed |

These are proposed technologies and may change during implementation.

## Evaluation Plan

The prototype should be evaluated on more than whether the graph looks convincing. Useful checks include:

- Extraction quality: Are the main events and entities identified correctly?
- Relationship quality: Are graph connections supported by evidence and sensible reasoning?
- Path quality: Are multi-step impact paths understandable and relevant?
- Historical comparison: Does the system accurately report what the selected market data shows during the chosen window?
- Transparency: Can users distinguish source facts from model inferences and hypothetical scenarios?
- Usability: Can a user enter an event, inspect the graph, and understand the explanation without specialist setup?

Any market comparison should specify the asset, benchmark where applicable, and time window. The prototype should avoid presenting a historical association as proof that the news event caused the price movement.

## Intended Users

- Financial analysts and researchers
- Students learning about financial markets
- Investors seeking to explore possible connections between events and assets
- Business and strategy teams assessing market developments

The system is an analytical support tool, not personalized financial advice or an automated trading guarantee.

## Future Scope

Possible future improvements include:

- Support for more reliable financial-news sources and market-data providers
- Live event monitoring and graph updates
- Stronger source verification and conflict detection
- Better benchmark-adjusted historical analysis
- More advanced scenario comparison
- Additional markets, sectors, and asset classes
- User accounts, saved investigations, and exportable reports

## Limitations

- News extraction can be incomplete or incorrect, so important relationships require validation.
- Historical data may be delayed, incomplete, or unavailable for some assets.
- Markets respond to many simultaneous factors; a price movement cannot automatically be attributed to one news event.
- Graph paths represent possible transmission mechanisms, not certain outcomes.
- LLM-generated explanations can be wrong and must be checked against their cited evidence.
- Confidence scores should not be interpreted as guaranteed prediction probabilities.

## Getting Started

This repository is intended to contain the implementation of the project. Setup instructions will be added once the application structure and dependencies are finalized.

A planned high-level structure is:

```text
autonomous-financial-event-market-impact-graph/
├── frontend/          # React + TypeScript dashboard
├── backend/           # FastAPI service and analysis logic
├── data/              # Small, permitted sample data only
├── docs/              # Design notes and project documentation
├── tests/             # Automated tests
├── .gitignore
└── README.md
```

Do not commit API keys, passwords, private datasets, or other secrets to the repository.

## Project Goal

Build a transparent financial-event analysis tool that helps users trace a possible market impact, inspect the reasoning behind it, and compare the hypothesis with historical evidence.
