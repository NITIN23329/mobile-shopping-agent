import { useMemo, useState } from "react";
import type { DebugEntry } from "@/hooks/useChat";
import { CircleAlert, Terminal } from "lucide-react";

interface DebugPanelProps {
  enabled: boolean;
  entries: DebugEntry[];
  sessionId?: string;
  apiBaseUrl: string;
  isSending: boolean;
  onClear: () => void;
}

// Lightweight developer-focused debug surface rendered only in debug mode.
const DebugPanel = ({ enabled, entries, sessionId, apiBaseUrl, isSending, onClear }: DebugPanelProps) => {
  const [open, setOpen] = useState(false);

  const formattedEntries = useMemo(() => entries.slice().reverse(), [entries]);

  if (!enabled) {
    return null;
  }

  return (
    <div className="fixed bottom-24 left-4 z-50 text-xs">
      <button
        type="button"
        className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white/90 px-3 py-1.5 font-medium text-slate-600 shadow-card transition hover:border-brand-300 hover:text-brand-600"
        onClick={() => setOpen((value) => !value)}
      >
        <Terminal className="h-4 w-4" aria-hidden />
        {open ? "Hide" : "Show"} debug
      </button>

      {open && (
        <div className="mt-3 w-80 rounded-3xl border border-slate-700 bg-slate-950/95 p-3 text-slate-100 shadow-2xl">
          <div className="flex items-center justify-between text-[11px] uppercase tracking-wide">
            <span className="text-brand-200">Debug stream</span>
            <button
              type="button"
              className="rounded-full border border-slate-700 px-2 py-1 text-[10px] font-semibold uppercase text-slate-300 transition hover:border-brand-400 hover:text-brand-200"
              onClick={onClear}
            >
              Clear
            </button>
          </div>

          <dl className="mt-3 space-y-1 text-[11px] text-slate-300">
            <div className="flex justify-between gap-2">
              <dt className="text-slate-500">Session</dt>
              <dd className="font-medium text-brand-200">{sessionId ?? "new"}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-slate-500">Backend</dt>
              <dd className="truncate font-medium text-brand-200" title={apiBaseUrl}>
                {apiBaseUrl}
              </dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-slate-500">Status</dt>
              <dd className={isSending ? "font-semibold text-amber-300" : "text-slate-300"}>
                {isSending ? "Sending…" : "Idle"}
              </dd>
            </div>
          </dl>

          <div className="mt-3 max-h-52 overflow-y-auto space-y-2">
            {formattedEntries.length === 0 ? (
              <p className="flex items-center gap-2 rounded-2xl bg-slate-800/70 px-3 py-2 text-[11px] text-slate-300">
                <CircleAlert className="h-3.5 w-3.5 text-slate-500" aria-hidden />
                No debug entries yet. Trigger a request to populate this feed.
              </p>
            ) : (
              formattedEntries.map((entry) => (
                <article
                  key={entry.id}
                  className="space-y-1 rounded-2xl border border-slate-800 bg-slate-900/80 px-3 py-2"
                >
                  <header className="flex items-center justify-between text-[10px] uppercase tracking-wide">
                    <span
                      className={entry.level === "error" ? "font-semibold text-red-400" : "text-brand-200"}
                    >
                      {entry.level}
                    </span>
                    <time className="text-slate-400" dateTime={entry.timestamp}>
                      {new Date(entry.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                    </time>
                  </header>
                  <p className="text-[11px] font-semibold text-slate-100">{entry.message}</p>
                  {entry.details && (
                    <pre className="max-h-28 overflow-auto whitespace-pre-wrap break-words rounded-xl bg-slate-900/70 p-2 text-[10px] text-slate-300">
                      {entry.details}
                    </pre>
                  )}
                </article>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DebugPanel;
