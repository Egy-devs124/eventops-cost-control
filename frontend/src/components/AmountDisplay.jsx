import { formatAmount } from "../utils/format";
import { useLanguage } from "../context/LanguageContext";

export function AmountDisplay({ value, muted = false }) {
  const { language } = useLanguage();
  return <span className={muted ? "amount muted" : "amount"}>{formatAmount(value, "EGP", language)}</span>;
}
