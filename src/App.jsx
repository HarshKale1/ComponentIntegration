import { useState } from "react";
import { api } from "./api/client";
import NewsInput from "./components/NewsInput";
import EventCard from "./components/EventCard";
import GraphView from "./components/GraphView";
import EvidenceDrawer from "./components/EvidenceDrawer";
import Legend from "./components/Legend";

export default function App() {
  const [graph, setGraph] = useState(null);
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedEdge, setSelectedEdge] = useState(null);

  const handleAnalyze = async (text) => {
    setLoading(true);
    setSelectedEdge(null);
    try {
      const res = await api.analyze(text);
      setEvent(res.event);
      setGraph({ nodes: res.nodes, edges: res.edges });
    } catch (err) {
      console.error(err);
      alert("Analysis failed. Check the console.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <header className="h-14 border-b border-slate-800 flex items-center px-6 bg-slate-950">
        <h1 className="text-lg font-bold tracking-tight">FinFlow AI</h1>
        <span className="ml-3 text-xs text-slate-500">
          Event → Market Impact
        </span>
        <span className="ml-auto text-xs text-slate-400 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          Ready
        </span>
      </header>

      <main className="p-6 grid grid-cols-12 gap-4">
        <div className="col-span-4 space-y-4">
          <NewsInput onAnalyze={handleAnalyze} loading={loading} />
          <EventCard event={event} />
          <Legend />
        </div>

        <div className="col-span-8 h-[calc(100vh-8rem)]">
          {graph ? (
            <GraphView graph={graph} onEdgeClick={setSelectedEdge} />
          ) : (
            <div className="w-full h-full flex items-center justify-center border border-dashed border-slate-700 rounded text-slate-500 text-sm">
              Paste a news event and click Analyze
            </div>
          )}
        </div>
      </main>

      {selectedEdge && (
        <EvidenceDrawer
          edge={selectedEdge}
          onClose={() => setSelectedEdge(null)}
        />
      )}
    </div>
  );
}