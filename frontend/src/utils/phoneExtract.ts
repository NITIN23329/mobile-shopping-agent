import type { PhoneRecord } from "@/types/api";

type JsonRecord = Record<string, unknown>;

export function extractPhonesFromEvents(rawResponse: Record<string, unknown> | undefined): PhoneRecord[] {
  if (!rawResponse) {
    return [];
  }

  const events = Array.isArray(rawResponse.events)
    ? rawResponse.events
    : [];
  const collected: PhoneRecord[] = [];
  const seen = new Set<string>();

  const visit = (value: unknown): void => {
    if (Array.isArray(value)) {
      value.forEach(visit);
      return;
    }
    if (!value || typeof value !== "object") {
      return;
    }

    const record = value as Record<string, unknown>;
    if (looksLikePhone(record)) {
      const entry = toPhoneRecord(record);
      const key = entry.id || `${entry.brand_name ?? ""}|${entry.phone_name ?? ""}`;
      if (key && !seen.has(key)) {
        collected.push(entry);
        seen.add(key);
      }
    }

    Object.values(record).forEach(visit);
  };

  visit(rawResponse);
  events.forEach(visit);

  return collected;
}

function looksLikePhone(value: Record<string, unknown>): boolean {
  if (!value) {
    return false;
  }
  const hasName = typeof value.phone_name === "string" || typeof value.brand_name === "string";
  const hasDetails =
    typeof value.price === "string" ||
    typeof value.image_url === "string" ||
    typeof value.spotlight === "object" ||
    typeof value.all_specs === "object";
  return hasName && hasDetails;
}

function toPhoneRecord(value: Record<string, unknown>): PhoneRecord {
  return {
    id: typeof value.id === "string" ? value.id : undefined,
    phone_name: typeof value.phone_name === "string" ? value.phone_name : undefined,
    brand_name: typeof value.brand_name === "string" ? value.brand_name : undefined,
    price: typeof value.price === "string" ? value.price : undefined,
    image_url: typeof value.image_url === "string" ? value.image_url : undefined,
    spotlight: toRecord(value.spotlight) ?? null,
    all_specs: toRecord(value.all_specs) ?? null,
  } satisfies PhoneRecord;
}

function toRecord(value: unknown): JsonRecord | undefined {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return undefined;
  }
  return value as JsonRecord;
}

export interface ComparisonRow {
  label: string;
  values: string[];
}

export function buildComparisonRows(phones: PhoneRecord[]): ComparisonRow[] {
  const descriptors: Array<{
    label: string;
    resolver: (phone: PhoneRecord) => string | undefined;
  }> = [
    {
      label: "Price",
      resolver: (phone) => phone.price,
    },
    {
      label: "Display",
  resolver: (phone) => getSpotlightField(phone, ["display", "screen_size"]),
    },
    {
      label: "Performance",
      resolver: (phone) => getSpotlightField(phone, ["summary", "performance"]),
    },
    {
      label: "RAM",
      resolver: (phone) => getSpotlightField(phone, ["ram_size", "memory"]),
    },
    {
      label: "Storage",
      resolver: (phone) => getSpotlightField(phone, ["storage", "storage_variants"]),
    },
    {
      label: "Battery",
      resolver: (phone) => getSpotlightField(phone, ["battery_size", "battery"]),
    },
    {
      label: "Rear Camera",
      resolver: (phone) => getSpotlightField(phone, ["rear_camera", "camera"]),
    },
    {
      label: "Front Camera",
      resolver: (phone) => getSpotlightField(phone, ["front_camera", "selfie_camera"]),
    },
    {
      label: "Software",
      resolver: (phone) => getSpotlightField(phone, ["software", "os_version"]),
    },
  ];

  return descriptors
    .map(({ label, resolver }) => ({
      label,
      values: phones.map((phone) => resolver(phone) || "—"),
    }))
    .filter((row) => row.values.some((value) => value && value !== "—"));
}

function getSpotlightField(phone: PhoneRecord, keys: string[]): string | undefined {
  const spotlight = toRecord(phone.spotlight);
  if (!spotlight) {
    return undefined;
  }
  for (const key of keys) {
    const value = spotlight[key];
    if (typeof value === "string") {
      return value;
    }
    if (Array.isArray(value)) {
      const flattened = value
        .map((item) => (typeof item === "string" ? item : undefined))
        .filter(Boolean)
        .join(", ");
      if (flattened) {
        return flattened;
      }
    }
  }
  return undefined;
}

export function buildPhoneHighlights(phone: PhoneRecord): Array<{ label: string; value: string }> {
  const highlights: Array<{ label: string; value: string }> = [];
  const spotlight = toRecord(phone.spotlight);

  const push = (label: string, value?: unknown) => {
    if (!value) {
      return;
    }
    if (typeof value === "string" && value.trim()) {
      highlights.push({ label, value: value.trim() });
      return;
    }
    if (Array.isArray(value)) {
      const text = value
        .map((entry) => (typeof entry === "string" ? entry : undefined))
        .filter(Boolean)
        .join(", ");
      if (text) {
        highlights.push({ label, value: text });
      }
    }
  };

  push("Display", spotlight?.display ?? spotlight?.screen_size);
  push("Performance", spotlight?.summary ?? spotlight?.performance);
  push("RAM", spotlight?.ram_size);
  push("Storage", spotlight?.storage);
  push("Battery", spotlight?.battery_size);
  push("Rear Camera", spotlight?.rear_camera ?? spotlight?.camera);
  push("Front Camera", spotlight?.front_camera ?? spotlight?.selfie_camera);

  return highlights.slice(0, 4);
}
