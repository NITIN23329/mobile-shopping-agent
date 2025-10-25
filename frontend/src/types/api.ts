export type ChatRole = "user" | "assistant" | "system";

export interface ChatRequestPayload {
  session_id: string;
  message: string;
}

export interface ChatResponsePayload {
  session_id: string;
  reply: string;
  raw_response: Record<string, unknown>;
}

export interface PhoneRecord {
  id?: string;
  phone_name?: string;
  brand_name?: string;
  price?: string;
  image_url?: string;
  spotlight?: Record<string, unknown> | null;
  all_specs?: Record<string, unknown> | null;
  [key: string]: unknown;
}

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: string;
  status?: "sending" | "error" | "done";
  phones?: PhoneRecord[];
  raw?: Record<string, unknown>;
  error?: string;
}
