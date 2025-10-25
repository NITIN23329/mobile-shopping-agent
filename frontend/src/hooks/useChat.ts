import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { sendChatMessage } from "@/api/chat";
import type { ChatMessage, ChatResponsePayload } from "@/types/api";
import { extractPhonesFromEvents } from "@/utils/phoneExtract";

const SESSION_STORAGE_KEY = "msa.sessionId";
const MAX_MESSAGES = 50;
const MAX_DEBUG_ENTRIES = 60;
const DEBUG_ENABLED = Boolean(import.meta.env.DEV || import.meta.env.VITE_DEBUG_LOGGING === "true");
const INVALID_SESSION_VALUES = new Set(["", "undefined", "null", "nan"]);
const DEFAULT_REQUEST_TIMEOUT_MS = 120_000;

const REQUEST_TIMEOUT_MS = (() => {
  const raw = Number.parseInt(import.meta.env.VITE_REQUEST_TIMEOUT_MS ?? "", 10);
  if (Number.isFinite(raw) && raw > 0) {
    return raw;
  }
  return DEFAULT_REQUEST_TIMEOUT_MS;
})();

type DebugLevel = "info" | "error";

export interface DebugEntry {
  id: string;
  timestamp: string;
  level: DebugLevel;
  message: string;
  details?: string;
}

type LogFn = (level: DebugLevel, message: string, details?: unknown) => void;

function now(): string {
  return new Date().toISOString();
}

function createSessionId(): string {
  try {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return crypto.randomUUID();
    }
  } catch (error) {
    console.debug("[useChat] Falling back to random session id", error);
  }
  return `session-${Math.random().toString(16).slice(2)}-${Date.now()}`;
}

function sanitizeSessionId(value: string | null | undefined): string | undefined {
  if (!value) {
    return undefined;
  }
  const trimmed = value.trim().replace(/^['"]+|['"]+$/g, "");
  if (!trimmed) {
    return undefined;
  }
  const lowered = trimmed.toLowerCase();
  if (INVALID_SESSION_VALUES.has(lowered)) {
    return undefined;
  }
  return trimmed;
}

export function useChat() {
  const [sessionId, setSessionId] = useState<string>(() => {
    try {
      const stored = sanitizeSessionId(localStorage.getItem(SESSION_STORAGE_KEY));
      if (stored) {
        return stored;
      }
    } catch (error) {
      console.warn("Unable to read session id from storage", error);
    }
    const generated = createSessionId();
    try {
      localStorage.setItem(SESSION_STORAGE_KEY, generated);
    } catch (error) {
      console.warn("Unable to persist generated session id", error);
    }
    return generated;
  });
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [debugEntries, setDebugEntries] = useState<DebugEntry[]>([]);
  const abortRef = useRef<AbortController | null>(null);
  const abortReasonRef = useRef<"timeout" | "cancel" | null>(null);

  const logDebug = useCallback<LogFn>((level, message, details) => {
    if (!DEBUG_ENABLED) {
      return;
    }

    const entry: DebugEntry = {
      id: crypto.randomUUID(),
      timestamp: now(),
      level,
      message,
      details: stringifyDetails(details),
    };

    setDebugEntries((prev) => {
      const next = [...prev, entry];
      if (next.length > MAX_DEBUG_ENTRIES) {
        return next.slice(next.length - MAX_DEBUG_ENTRIES);
      }
      return next;
    });

    const consoleMethod = level === "error" ? console.error : console.debug;
    if (details !== undefined) {
      consoleMethod(`[useChat] ${message}`, details);
    } else {
      consoleMethod(`[useChat] ${message}`);
    }
  }, []);

  useEffect(() => {
    const sanitized = sanitizeSessionId(sessionId) ?? createSessionId();
    if (sanitized !== sessionId) {
      setSessionId(sanitized);
    }
    try {
      localStorage.setItem(SESSION_STORAGE_KEY, sanitized);
    } catch (error) {
      console.warn("Unable to persist session id", error);
    }
    logDebug("info", "Session id synced to storage", sanitized);
  }, [sessionId, logDebug]);

  useEffect(() => {
    return () => {
      if (abortRef.current) {
        abortRef.current.abort();
        logDebug("info", "Aborted inflight request on unmount");
      }
    };
  }, [logDebug]);

  const upsertAssistantMessage = useCallback(
    (assistantId: string, updater: (message: ChatMessage) => ChatMessage) => {
      setMessages((prev) =>
        prev.map((message) =>
          message.id === assistantId ? updater(message) : message,
        ),
      );
    },
  []);

  const sendMessage = useCallback(
    async (text: string): Promise<boolean> => {
      const trimmed = text.trim();
      if (!trimmed || isSending) {
        logDebug("info", "Blocked send: empty input or already sending", {
          trimmedLength: trimmed.length,
          isSending,
        });
        return false;
      }

      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmed,
        timestamp: now(),
        status: "done",
      };
      const assistantId = crypto.randomUUID();
      const placeholder: ChatMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        timestamp: now(),
        status: "sending",
      };

      setMessages((prev) => {
        const next = [...prev, userMessage, placeholder];
        if (next.length > MAX_MESSAGES) {
          return next.slice(next.length - MAX_MESSAGES);
        }
        return next;
      });

      setIsSending(true);
      const controller = new AbortController();
      abortRef.current = controller;
      abortReasonRef.current = null;
      const timeoutId = window.setTimeout(() => {
        if (!controller.signal.aborted) {
          abortReasonRef.current = "timeout";
          controller.abort();
          logDebug("error", "Request aborted due to timeout", {
            timeoutMs: REQUEST_TIMEOUT_MS,
          });
        }
      }, REQUEST_TIMEOUT_MS);

      let succeeded = false;
      try {
        const nextSessionId = sanitizeSessionId(sessionId) ?? createSessionId();
        if (sessionId !== nextSessionId) {
          setSessionId(nextSessionId);
        }

        const payload = {
          message: trimmed,
          session_id: nextSessionId,
        };
        logDebug("info", "Dispatching chat request", payload);
        const response = await sendChatMessage(payload, controller.signal);
        persistSessionId(response, setSessionId, logDebug);
        const phones = extractPhonesFromEvents(response.raw_response);

        logDebug("info", "Received agent response", {
          sessionId: response.session_id,
          replyLength: response.reply?.length ?? 0,
          phoneCount: phones.length,
        });

        succeeded = true;

        upsertAssistantMessage(assistantId, (message) => ({
          ...message,
          status: "done",
          content: response.reply,
          phones,
          raw: response.raw_response,
        }));
      } catch (error) {
        let errorMessage: string;
        if (error instanceof DOMException && error.name === "AbortError") {
          if (abortReasonRef.current === "timeout") {
            errorMessage = `Request timed out after ${Math.round(REQUEST_TIMEOUT_MS / 1000)}s`;
          } else if (abortReasonRef.current === "cancel") {
            errorMessage = "Request cancelled";
          } else {
            errorMessage = "Request aborted";
          }
        } else if (error instanceof Error) {
          errorMessage = error.message;
        } else {
          errorMessage = "Unknown error";
        }

        logDebug("error", "Failed to send message", errorMessage);
        upsertAssistantMessage(assistantId, (message) => ({
          ...message,
          status: "error",
          error: errorMessage,
        }));
        succeeded = false;
      } finally {
        setIsSending(false);
        abortRef.current = null;
        abortReasonRef.current = null;
        window.clearTimeout(timeoutId);
      }

      return succeeded;
    },
    [isSending, sessionId, upsertAssistantMessage, logDebug],
  );

  const cancel = useCallback(() => {
    if (abortRef.current) {
      abortReasonRef.current = "cancel";
      abortRef.current.abort();
      abortRef.current = null;
      setIsSending(false);
      logDebug("info", "User cancelled the active request");
    }
  }, [logDebug]);

  const resetSession = useCallback(() => {
    const fresh = createSessionId();
    setSessionId(fresh);
    setMessages([]);
    logDebug("info", "Session reset by user");
  }, [logDebug]);

  const state = useMemo(
    () => ({
      messages,
      isSending,
      sessionId,
    }),
    [messages, isSending, sessionId],
  );

  const clearDebug = useCallback(() => {
    setDebugEntries([]);
  }, []);

  return {
    ...state,
    sendMessage,
    cancel,
    resetSession,
    debug: {
      enabled: DEBUG_ENABLED,
      entries: debugEntries,
      clear: clearDebug,
    },
  } as const;
}

function persistSessionId(
  response: ChatResponsePayload,
  setter: (value: string) => void,
  logger?: LogFn,
): void {
  const sanitized = sanitizeSessionId(response.session_id);
  if (!sanitized) {
    logger?.("error", "Received invalid session id from response", response.session_id);
    return;
  }
  setter(sanitized);
  logger?.("info", "Session id updated", sanitized);
}

function stringifyDetails(value: unknown): string | undefined {
  if (value === undefined || value === null) {
    return undefined;
  }
  if (typeof value === "string") {
    return value;
  }
  try {
    const json = JSON.stringify(value);
    if (!json) {
      return undefined;
    }
    return json.length > 400 ? `${json.slice(0, 397)}…` : json;
  } catch (error) {
    console.debug("[useChat] Failed to stringify debug details", error);
    return String(value);
  }
}
