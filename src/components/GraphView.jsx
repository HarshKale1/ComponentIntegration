import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";
import { strengthColor, nodeColor } from "../utils/colors";

export default function GraphView({ graph, onEdgeClick }) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !graph) return;

    const elements = [
      ...graph.nodes.map((n) => ({
        data: { id: n.id, label: n.label, type: n.type },
      })),
      ...graph.edges.map((e) => ({ data: e })),
    ];

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: "node",
          style: {
            "background-color": (ele) => nodeColor(ele.data("type")),
            label: "data(label)",
            color: "#e2e8f0",
            "font-size": 11,
            "text-valign": "bottom",
            "text-margin-y": 4,
            "text-outline-color": "#020617",
            "text-outline-width": 2,
            width: 34,
            height: 34,
            "border-width": 2,
            "border-color": "#0f172a",
          },
        },
        {
          selector: "edge",
          style: {
            width: (ele) => 1 + ele.data("strength") * 5,
            "line-color": (ele) => strengthColor(ele.data("strength")),
            "target-arrow-color": (ele) =>
              strengthColor(ele.data("strength")),
            "target-arrow-shape": "triangle",
            "arrow-scale": 1,
            "curve-style": "bezier",
            opacity: 0.9,
          },
        },
        {
          selector: "edge[evidence_type = 'HYPOTHESIS']",
          style: { "line-style": "dashed" },
        },
      ],
      layout: {
        name: "cose",
        animate: true,
        padding: 40,
        nodeRepulsion: 8000,
        idealEdgeLength: 100,
      },
      wheelSensitivity: 0.2,
    });

    cy.on("tap", "edge", (evt) => {
      if (onEdgeClick) onEdgeClick(evt.target.data());
    });

    cyRef.current = cy;

    return () => cy.destroy();
  }, [graph, onEdgeClick]);

  return (
    <div
      ref={containerRef}
      className="w-full h-full bg-slate-900 rounded border border-slate-800"
    />
  );
}