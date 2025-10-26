import { useCallback, useEffect, useRef, useState } from "react";
import ChatHeader from "@/components/ChatHeader";
import DebugPanel from "@/components/DebugPanel";
import MessageBubble from "@/components/MessageBubble";
import MessageComposer from "@/components/MessageComposer";
import LoadingDots from "@/components/LoadingDots";
import { API_BASE_URL } from "@/api/chat";
import { useChat } from "@/hooks/useChat";
import type { ChatMessage } from "@/types/api";

const SUGGESTED_PROMPTS = [
  "Best camera phone under ₹30,000",
  "Compare Pixel 9a vs OnePlus 13R",
  "Compact Android with excellent one-hand use",
  "Explain OIS vs EIS in simple terms",
];

function App() {
  const { messages, sessionId, sendMessage, isSending, cancel, resetSession, debug } = useChat();
  const [input, setInput] = useState("");
  const [copyState, setCopyState] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [messages]);

  const handleSubmit = useCallback(
    async (value: string): Promise<boolean> => {
      const trimmed = value.trim();
      if (!trimmed) {
        return false;
      }
      setInput("");
      const success = await sendMessage(trimmed);
      if (!success) {
        setInput(trimmed);
      }
      return success;
    },
    [sendMessage],
  );

  const handleCopy = useCallback(async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopyState("Copied to clipboard");
      setTimeout(() => setCopyState(null), 2500);
    } catch (error) {
      console.warn("Clipboard unavailable", error);
      setCopyState("Copy failed");
      setTimeout(() => setCopyState(null), 2500);
    }
  }, []);

  const handleSuggestion = useCallback(
    (prompt: string) => {
      void handleSubmit(prompt);
    },
    [handleSubmit],
  );

  const emptyState = messages.length === 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-white to-brand-100/40 text-slate-900">
      <ChatHeader />
      <main className="mx-auto flex max-w-4xl flex-col gap-6 px-4 pb-40 pt-6 sm:px-6">
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-3xl border border-brand-100/60 bg-white/80 px-4 py-3 text-xs text-slate-500 sm:text-sm">
          <span>
            Session <strong className="font-semibold text-brand-700">{sessionId ?? "new"}</strong>
          </span>
          {isSending && (
            <span className="flex items-center gap-2 text-brand-600">
              <LoadingDots />
              <span>Crafting a recommendation…</span>
            </span>
          )}
        </div>

        {emptyState ? (
          <section className="rounded-3xl border border-slate-200 bg-white/90 p-6 shadow-card">
            <h2 className="font-display text-lg font-semibold text-slate-900">
              Ask me anything about smartphones
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              I can surface the best options, explain features, and compare phones side-by-side.
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {SUGGESTED_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => handleSuggestion(prompt)}
                  className="rounded-3xl border border-transparent bg-brand-50/70 px-4 py-3 text-left text-sm text-brand-700 transition hover:border-brand-200 hover:bg-brand-100"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </section>
        ) : (
          messages.map((message: ChatMessage) => (
            <MessageBubble key={message.id} message={message} onCopy={handleCopy} />
          ))
        )}
        <div ref={endRef} />
      </main>

      <MessageComposer
        value={input}
        onChange={setInput}
        onSubmit={handleSubmit}
        onCancel={cancel}
        onReset={resetSession}
        disabled={isSending}
      />

      {copyState && (
        <div className="pointer-events-none fixed inset-x-0 bottom-24 flex justify-center px-4">
          <div className="rounded-full bg-slate-900/90 px-4 py-2 text-xs font-medium text-white shadow-lg">
            {copyState}
          </div>
        </div>
      )}

      <DebugPanel
        enabled={debug.enabled}
        entries={debug.entries}
        sessionId={sessionId}
        apiBaseUrl={API_BASE_URL}
        isSending={isSending}
        onClear={debug.clear}
      />
    </div>
  );
}

export default App;
