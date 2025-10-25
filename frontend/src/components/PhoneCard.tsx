import type { FC } from "react";
import { ImageOff } from "lucide-react";
import type { PhoneRecord } from "@/types/api";
import { buildPhoneHighlights } from "@/utils/phoneExtract";

interface PhoneCardProps {
  phone: PhoneRecord;
}

const PhoneCard: FC<PhoneCardProps> = ({ phone }) => {
  const highlights = buildPhoneHighlights(phone);
  const imageUrl = phone.image_url || undefined;

  return (
    <article className="group flex flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white/90 shadow-card transition hover:-translate-y-1 hover:shadow-lg">
      <div className="relative h-36 w-full bg-gradient-to-br from-brand-100 via-white to-brand-200">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={phone.phone_name ?? "Phone"}
            loading="lazy"
            className="absolute inset-0 h-full w-full object-contain p-4 transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-brand-600/70">
            <ImageOff className="h-12 w-12" aria-hidden />
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-3 px-5 pb-5 pt-4">
        <div className="space-y-1">
          <p className="text-xs uppercase tracking-[0.2em] text-brand-600/80">
            {phone.brand_name || "Brand"}
          </p>
          <h3 className="font-display text-lg font-semibold text-slate-900">
            {phone.phone_name || "Unnamed phone"}
          </h3>
          {phone.price && (
            <p className="text-sm font-medium text-brand-700">{phone.price}</p>
          )}
        </div>

        {highlights.length > 0 && (
          <ul className="grid gap-2">
            {highlights.map((highlight) => (
              <li
                key={`${phone.id ?? phone.phone_name}-${highlight.label}`}
                className="flex items-start gap-2 rounded-2xl bg-brand-50/80 px-3 py-2 text-xs text-slate-700"
              >
                <span className="font-semibold text-brand-800">{highlight.label}:</span>
                <span className="text-slate-600">{highlight.value}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </article>
  );
};

export default PhoneCard;
