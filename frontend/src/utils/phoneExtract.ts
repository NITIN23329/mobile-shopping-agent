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

export function buildPhoneSummary(phone: PhoneRecord): {
  memory?: string;
  chipset?: string;
  price?: string;
} {
  const ram = getSpotlightField(phone, ["ram_size", "memory"]);
  const storage = getSpotlightField(phone, ["storage", "storage_options", "storage_variants"]);
  const chipsetRaw = extractChipset(phone);
  const priceRaw = phone.price;

  const memory = joinParts(formatSummaryValue(ram), formatSummaryValue(storage), " / ");
  const chipset = formatSummaryValue(chipsetRaw, 40);
  const price = formatSummaryValue(extractPrimaryPrice(priceRaw), 32);

  return { memory, chipset, price };
}

function extractChipset(phone: PhoneRecord): string | undefined {
  const spotlight = toRecord(phone.spotlight);
  const candidates: unknown[] = [];

  if (spotlight) {
    candidates.push(
      spotlight.chipset,
      spotlight.processor,
      spotlight.performance,
      spotlight.summary,
    );
  }

  for (const candidate of candidates) {
    const text = normalizeValue(candidate);
    if (text) {
      return text;
    }
  }

  const allSpecs = toRecord(phone.all_specs);
  if (!allSpecs) {
    return undefined;
  }

  const sections = ["Performance", "Platform", "Hardware"];
  for (const section of sections) {
    const entries = allSpecs[section];
    if (!Array.isArray(entries)) {
      continue;
    }
    for (const entry of entries) {
      if (!entry || typeof entry !== "object") {
        continue;
      }
      const label = normalizeValue(
        (entry as JsonRecord).title ||
          (entry as JsonRecord).label ||
          (entry as JsonRecord).name ||
          (entry as JsonRecord).spec,
      );
      const info = normalizeValue(
        (entry as JsonRecord).info ||
          (entry as JsonRecord).value ||
          (entry as JsonRecord).details,
      );

      if (!label) {
        continue;
      }

      const lowerLabel = label.toLowerCase();
      if (lowerLabel.includes("chipset") || lowerLabel.includes("processor")) {
        return info || label;
      }
      if (!info) {
        continue;
      }
      if (lowerLabel.includes("cpu") || lowerLabel.includes("platform")) {
        return info;
      }
    }
  }

  return undefined;
}

function normalizeValue(value: unknown): string | undefined {
  if (!value) {
    return undefined;
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed || undefined;
  }
  if (Array.isArray(value)) {
    const joined = value
      .map((item) => (typeof item === "string" ? item.trim() : undefined))
      .filter(Boolean)
      .join(", ");
    return joined || undefined;
  }
  if (typeof value === "object") {
    const record = value as JsonRecord;
    const parts = [record.text, record.value, record.info]
      .map((part) => (typeof part === "string" ? part.trim() : undefined))
      .filter(Boolean)
      .join(" ");
    return parts || undefined;
  }
  return undefined;
}

function extractPrimaryPrice(priceText: string | undefined): string | undefined {
  if (!priceText) {
    return undefined;
  }
  const currencyMatch = priceText.match(/(?:₹|rs\.?|inr)\s*([\d,]+)/i);
  if (currencyMatch) {
    return `₹${currencyMatch[1]}`;
  }
  const numberMatch = priceText.match(/\b(\d[\d,]{3,})\b/);
  if (numberMatch) {
    return numberMatch[1];
  }
  return priceText.split(/[|,]/)[0]?.trim() || undefined;
}

function formatSummaryValue(value: string | undefined, maxLength = 30): string | undefined {
  if (!value) {
    return undefined;
  }
  const firstSegment = value.split(/\s*[|•;/]\s*|,\s*/)[0]?.trim() || value.trim();
  if (!firstSegment) {
    return undefined;
  }
  if (firstSegment.length <= maxLength) {
    return firstSegment;
  }
  return `${firstSegment.slice(0, maxLength - 1)}…`;
}

function joinParts(left?: string, right?: string, separator = " "): string | undefined {
  const parts = [left, right].filter((part): part is string => Boolean(part));
  if (parts.length === 0) {
    return undefined;
  }
  return parts.join(separator);
}
