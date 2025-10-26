import type { FormEvent, KeyboardEvent } from "react";
import { CircleStop, RotateCcw, Send } from "lucide-react";
import clsx from "clsx";

interface MessageComposerProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (value: string) => void | Promise<unknown>;
  onCancel: () => void;
  onReset: () => void;
  disabled?: boolean;
}

const MessageComposer = ({
  value,
  onChange,
  onSubmit,
  onCancel,
  onReset,
  disabled,
}: MessageComposerProps) => {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void onSubmit(value);
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void onSubmit(value);
    }
  };

  return (
    <div className="fixed inset-x-0 bottom-0 border-t border-slate-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-4xl flex-col gap-3 px-4 py-4 sm:px-6">
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <textarea
            value={value}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about cameras, battery life, budgets, or phone comparisons..."
            rows={4}
            className="w-full resize-none rounded-3xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-brand-400 focus:shadow-glow"
            spellCheck={true}
            maxLength={2000}
            disabled={disabled}
          />
          <div className="flex flex-col items-stretch gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
              <button
                type="button"
                onClick={onReset}
                className="inline-flex w-full items-center justify-center gap-2 rounded-full border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-500 transition hover:border-brand-400 hover:text-brand-600 sm:w-auto"
              >
                <RotateCcw className="h-4 w-4" aria-hidden />
                New session
              </button>
              {disabled && (
                <button
                  type="button"
                  onClick={onCancel}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-full border border-transparent bg-brand-100 px-3 py-1.5 text-xs font-semibold text-brand-700 transition hover:bg-brand-200 sm:w-auto"
                >
                  <CircleStop className="h-4 w-4" aria-hidden />
                  Cancel
                </button>
              )}
            </div>
            <button
              type="submit"
              className={clsx(
                "inline-flex w-full items-center justify-center gap-2 rounded-full bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-card transition sm:w-auto",
                disabled && "opacity-60",
              )}
              disabled={disabled}
            >
              Send <Send className="h-4 w-4" aria-hidden />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MessageComposer;
