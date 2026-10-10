export default function EventCard({ event }) {
  if (!event) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded p-4">
      <p className="text-xs uppercase tracking-wider text-emerald-400">
        {event.event_type?.replace(/_/g, " ")}
      </p>
      <h2 className="text-base font-semibold mt-1 leading-snug">
        {event.headline}
      </h2>
      <p className="text-xs text-slate-500 mt-1">Source: {event.source}</p>
      <p className="text-sm text-slate-300 mt-2 leading-relaxed">
        {event.summary}
      </p>
    </div>
  );
}