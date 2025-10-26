import type { FC } from "react";
import type { PhoneRecord } from "@/types/api";
import { buildComparisonRows } from "@/utils/phoneExtract";

interface ComparisonTableProps {
  phones: PhoneRecord[];
}

const ComparisonTable: FC<ComparisonTableProps> = ({ phones }) => {
  const rows = buildComparisonRows(phones);

  if (rows.length === 0) {
    return null;
  }

  return (
    <div className="rounded-3xl border border-slate-200 bg-white shadow-card">
      <div className="w-full overflow-x-auto px-2 pb-2">
        <table className="w-full text-left text-xs text-slate-700 sm:text-sm">
          <thead className="bg-brand-100/70 text-[11px] uppercase tracking-wide text-brand-800 sm:text-xs">
          <tr>
              <th className="px-3 py-2 sm:px-4 sm:py-3">Feature</th>
            {phones.map((phone) => (
                <th key={phone.id ?? phone.phone_name} className="px-3 py-2 sm:px-4 sm:py-3">
                  <div className="space-y-0.5 text-[11px] sm:text-sm">
                    <p className="font-semibold text-slate-900">{phone.phone_name}</p>
                    <p className="text-[10px] text-brand-700 sm:text-xs">{phone.brand_name}</p>
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label} className="border-t border-slate-100">
                <th className="bg-slate-50/70 px-3 py-2 text-left font-semibold text-slate-800 sm:px-4 sm:py-3">
                {row.label}
              </th>
              {row.values.map((value, index) => (
                  <td key={`${row.label}-${index}`} className="px-3 py-2 align-top text-slate-600 sm:px-4 sm:py-3">
                  {value}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
        </table>
      </div>
    </div>
  );
};

export default ComparisonTable;
