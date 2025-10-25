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
    <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-card">
      <table className="w-full text-left text-sm text-slate-700">
        <thead className="bg-brand-100/70 text-xs uppercase tracking-wide text-brand-800">
          <tr>
            <th className="px-4 py-3">Feature</th>
            {phones.map((phone) => (
              <th key={phone.id ?? phone.phone_name} className="px-4 py-3">
                <div className="space-y-0.5">
                  <p className="font-semibold text-slate-900">{phone.phone_name}</p>
                  <p className="text-xs text-brand-700">{phone.brand_name}</p>
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label} className="border-t border-slate-100">
              <th className="bg-slate-50/70 px-4 py-3 font-semibold text-slate-800">
                {row.label}
              </th>
              {row.values.map((value, index) => (
                <td key={`${row.label}-${index}`} className="px-4 py-3 align-top text-slate-600">
                  {value}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ComparisonTable;
