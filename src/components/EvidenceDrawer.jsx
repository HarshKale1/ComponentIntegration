import {
  strengthColor,
  strengthLabel,
  directionLabel,
  evidenceTypeLabel,
} from "../utils/colors";

export default function EvidenceDrawer({ edge, onClose }) {
  if (!edge) return null;

  const color = strengthColor(edge.strength);

  return (
    <div className="fixed right-0 top-0 h-full w-[400px] bg-slate-900 border-l border-slate-700 p-5 overflow-y-auto z-50 shadow-2xl">
      <div className="flex justify-between items-start">
        <h3 className="text-base font-semibold">Relationship Detail</h3>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white text-lg leading-none"
        >
          ✕
        </button>
      </div>

      <p className="text-sm text-slate-300 mt-4">
        <span className="text-white font-medium">{edge.source}</span>
        <span className="mx-2 text-slate-500">→</span>
        <span className="text-white font-medium">{edge.target}</span>
      </p>
      <p className="text-xs text-emerald-400 mt-1">{edge.relationship}</p>

      <div className="flex flex-wrap gap-2 mt-3">
        <span
          className="text-xs px-2 py-0.5 rounded font-medium"
          style={{ backgroundColor: color + "33", color }}
        >
          {strengthLabel(edge.strength)} · {edge.strength.toFixed(2)}
        </span>
        <span className="text-xs px-2 py-0.5 rounded bg-slate-800">
          {directionLabel(edge.effect_direction)}
        </span>
        <span className="text-xs px-2 py-0.5 rounded bg-slate-800">
          {evidenceTypeLabel(edge.evidence_type)}
        </span>
      </div>

      <section className="mt-5">
        <h4 className="text-xs uppercase text-slate-500 tracking-wider">
          Explanation
        </h4>
        <p className="text-sm mt-1 text-slate-200 leading-relaxed">
          {edge.explanation}
        </p>
      </section>

      <section className="mt-5">
        <h4 className="text-xs uppercase text-slate-500 tracking-wider">
          Evidence
        </h4>
        {edge.evidence?.length ? (
          <ul className="mt-1 space-y-2">
            {edge.evidence.map((ev, i) => (
              <li
                key={i}
                className="border-l-2 border-slate-700 pl-3 text-sm text-slate-200"
              >
                {ev.text}
                <span className="text-xs text-slate-500 block mt-0.5">
                  — {ev.source}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500 italic mt-1">
            Insufficient verified evidence.
          </p>
        )}
      </section>

      <section className="mt-5">
        <h4 className="text-xs uppercase text-slate-500 tracking-wider">
          Historical Examples
        </h4>
        {edge.historical_examples?.length ? (
          <ul className="mt-1 space-y-2">
            {edge.historical_examples.map((h, i) => (
              <li
                key={i}
                className="border border-slate-800 rounded p-2 text-sm"
              >
                <p className="font-medium">{h.event}</p>
                <p className="text-xs text-slate-500">{h.date}</p>
                <p className="text-xs text-slate-400 mt-1">{h.outcome}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500 italic mt-1">
            No verified historical analogues.
          </p>
        )}
      </section>

      <section className="mt-5">
        <h4 className="text-xs uppercase text-slate-500 tracking-wider">
          Limitations
        </h4>
        {edge.limitations?.length ? (
          <ul className="mt-1 text-sm space-y-1 list-disc list-inside text-slate-300">
            {edge.limitations.map((l, i) => (
              <li key={i}>{l}</li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500 italic mt-1">
            None recorded.
          </p>
        )}
      </section>
    </div>
  );
}