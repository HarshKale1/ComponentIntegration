import { useState } from "react";

export default function NewsInput({ onAnalyze, loading }) {
  const [text, setText] = useState("");

  const submit = () => {
    if (text.trim()) onAnalyze(text);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded p-4">
      <label className="text-xs uppercase text-slate-400 tracking-wider">
        Paste Financial News
      </label>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={3}
        placeholder="e.g. Brent crude surges 12% after OPEC+ supply cut"
        className="w-full mt-2 bg-slate-950 border border-slate-700 rounded p-3 text-sm focus:outline-none focus:border-emerald-500 resize-none"
      />

      <div className="flex flex-wrap gap-2 mt-3">
        <button
          onClick={submit}
          disabled={loading}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed rounded text-sm font-medium transition-colors"
        >
          {loading ? "Analyzing…" : "Analyze Event"}
        </button>

        <button
          onClick={() => setText("Brent crude surges 12% after OPEC+ supply cut")}
          className="px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded text-xs transition-colors"
        >
          Try: Crude
        </button>

        <button
          onClick={() => setText("RBI holds repo rate at 6.5%")}
          className="px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded text-xs transition-colors"
        >
          Try: RBI rate
        </button>
      </div>
    </div>
  );
}
