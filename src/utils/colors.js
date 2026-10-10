// ---- Edge strength colors (muted palette) ----
export const strengthColor = (s) => {
  if (s >= 0.7) return "#e05c5c"; // strong — muted coral
  if (s >= 0.4) return "#d99a4a"; // medium — burnished amber
  return "#5fb87f";               // weak — sage green
};

export const strengthLabel = (s) => {
  if (s >= 0.7) return "Strong";
  if (s >= 0.4) return "Medium";
  return "Weak";
};

// ---- Node type colors (cohesive family) ----
export const nodeColor = (type) =>
  ({
    event: "#9d7fe8",      // soft violet
    country: "#5b8def",    // calm blue
    commodity: "#e08d5c",  // terracotta
    indicator: "#d4c060",  // muted gold
    sector: "#4fb3a8",     // sea green
    company: "#dd78ab",    // dusty rose
    instrument: "#8b95a7", // muted gray
  }[type] || "#8b95a7");

// ---- Direction labels ----
export const directionLabel = (d) =>
  ({
    positive: "▲ Positive",
    negative: "▼ Negative",
    neutral: "— Neutral",
    conditional: "◇ Conditional",
    uncertain: "? Uncertain",
  }[d] || d);

// ---- Evidence type labels ----
export const evidenceTypeLabel = (t) =>
  ({
    observed_fact: "Observed fact",
    established_relationship: "Established relationship",
    economic_mechanism: "Economic mechanism",
    inferred_hypothesis: "Inferred hypothesis",
  }[t] || t);