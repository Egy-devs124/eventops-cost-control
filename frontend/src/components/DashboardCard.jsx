import { ArrowUpRight } from "lucide-react";

import { AmountDisplay } from "./AmountDisplay";
import { useLanguage } from "../context/LanguageContext";
import { formatNumber } from "../utils/format";

export function DashboardCard({ title, value, amount = false, icon: Icon = ArrowUpRight, tone = "neutral" }) {
  const { language } = useLanguage();
  return (
    <article className={`dashboard-card ${tone}`}>
      <div className="card-icon" aria-hidden="true">
        <Icon size={20} />
      </div>
      <div>
        <span>{title}</span>
        <strong>{amount ? <AmountDisplay value={value} /> : formatNumber(value, language)}</strong>
      </div>
    </article>
  );
}
