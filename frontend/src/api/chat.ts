import type { ChatRequestPayload, ChatResponsePayload } from "@/types/api";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000";

export async function sendChatMessage(payload: ChatRequestPayload, signal?: AbortSignal): Promise<ChatResponsePayload> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    signal,
  });

  if (!response.ok) {
    const detail = await safeReadText(response);
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

async function safeReadText(res: Response): Promise<string | undefined> {
  try {
    return await res.text();
  } catch (error) {
    console.error("Failed to read error body", error);
    return undefined;
  }
}
