import { titleFromKey } from "../utils/format";
import { useLanguage } from "../context/LanguageContext";

export function StatusBadge({ value, namespace = "status" }) {
  const { t } = useLanguage();
  const normalized = String(value || "");
  const tone = normalized.includes("paid") || ["accepted", "approved", "completed", "confirmed", "done"].includes(normalized)
    ? "success"
    : normalized.includes("cancel") || normalized.includes("reject") || normalized.includes("blocked") || normalized.includes("overdue")
      ? "danger"
      : normalized.includes("pending") || normalized.includes("waiting") || normalized.includes("draft")
        ? "warning"
        : "neutral";
  return <span className={`status-badge ${tone}`}>{t(`${namespace}.${value}`, t(`status.${value}`, titleFromKey(value)))}</span>;
}
