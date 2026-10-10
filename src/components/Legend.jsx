export default function Legend() {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded p-4">
      <h3 className="text-xs uppercase text-slate-400 tracking-wider mb-3">
        Legend
      </h3>

      <div className="space-y-2 text-xs">
        <div className="flex items-center gap-2">
          <span className="w-6 h-1 bg-red-500 rounded" />
          <span>Strong (≥ 0.70)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-6 h-1 bg-amber-500 rounded" />
          <span>Medium (0.40 – 0.69)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-6 h-1 bg-green-500 rounded" />
          <span>Weak (&lt; 0.40)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-6 h-0 border-t border-dashed border-slate-400" />
          <span>Inferred hypothesis</span>
        </div>
      </div>
    </div>
  );
}