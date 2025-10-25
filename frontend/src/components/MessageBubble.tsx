import { useState } from "react";
import clsx from "clsx";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChevronDown, ChevronUp, Copy, ShieldAlert } from "lucide-react";
import type { FC } from "react";
import type { ChatMessage } from "@/types/api";
import PhoneCard from "@/components/PhoneCard";
import ComparisonTable from "@/components/ComparisonTable";
import LoadingDots from "@/components/LoadingDots";

interface MessageBubbleProps {
  message: ChatMessage;
  onCopy?: (text: string) => void;
}

const MessageBubble: FC<MessageBubbleProps> = ({ message, onCopy }) => {
  const [showDetails, setShowDetails] = useState(false);
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";
  const showComparison = (message.phones?.length ?? 0) >= 2 && (message.phones?.length ?? 0) <= 3;

  const bubbleClass = clsx(
    "max-w-xl rounded-3xl px-5 py-4 text-sm shadow-card",
    isUser
      ? "ml-auto bg-brand-600 text-white"
      : "mr-auto bg-white/95 text-slate-800 border border-slate-200",
  );

  const handleCopy = () => {
    if (!onCopy || !message.content) {
      return;
    }
    onCopy(message.content);
  };

  return (
    <div className="flex flex-col gap-4">
      <div className={clsx("flex", isUser ? "justify-end" : "justify-start")}
        aria-live={message.status === "sending" ? "polite" : undefined}
      >
        <div className="space-y-3">
          <div className={bubbleClass}>
            {message.status === "error" ? (
              <div className="flex items-start gap-3 text-sm">
                <ShieldAlert className="h-5 w-5 text-red-500" aria-hidden />
                <div>
                  <p className="font-semibold text-red-600">Something went wrong</p>
                  <p className="text-red-500/90">{message.error || "The agent could not respond."}</p>
                </div>
              </div>
            ) : message.status === "sending" && !message.content ? (
              <LoadingDots className={isUser ? "justify-end" : "justify-start"} />
            ) : (
              <article className="prose prose-sm max-w-none text-current prose-p:my-3 prose-headings:mt-4 prose-headings:font-semibold prose-headings:text-slate-900 prose-strong:text-brand-700 prose-a:text-brand-600">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
              </article>
            )}
          </div>

          {isAssistant && message.content && (
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <time dateTime={message.timestamp}>
                {new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </time>
              {onCopy && (
                <button
                  type="button"
                  className="inline-flex items-center gap-1 rounded-full border border-slate-200 px-3 py-1 text-xs font-medium text-slate-500 transition hover:border-brand-400 hover:text-brand-600"
                  onClick={handleCopy}
                >
                  <Copy className="h-4 w-4" aria-hidden /> Copy reply
                </button>
              )}
              {message.raw && (
                <button
                  type="button"
                  className="inline-flex items-center gap-1 rounded-full border border-slate-200 px-3 py-1 text-xs font-medium text-slate-500 transition hover:border-brand-400 hover:text-brand-600"
                  onClick={() => setShowDetails((value) => !value)}
                >
                  {showDetails ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  {showDetails ? "Hide" : "View"} raw data
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {isAssistant && message.phones && message.phones.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2">
          {message.phones.slice(0, 4).map((phone) => (
            <PhoneCard key={phone.id ?? phone.phone_name} phone={phone} />
          ))}
        </div>
      )}

      {isAssistant && showComparison && message.phones && (
        <ComparisonTable phones={message.phones.slice(0, 3)} />
      )}

      {showDetails && message.raw && (
        <pre className="max-h-72 overflow-auto rounded-3xl border border-slate-200 bg-slate-950/95 p-4 text-xs text-slate-100">
          {JSON.stringify(message.raw, null, 2)}
        </pre>
      )}
    </div>
  );
};

export default MessageBubble;
