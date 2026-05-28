function currentLanguage(language) {
  return language || localStorage.getItem("eventops.language") || "en";
}

export function localeFor(language) {
  return currentLanguage(language) === "ar" ? "ar-EG" : "en-EG";
}

export function formatAmount(value, currency = "EGP", language) {
  const amount = Number(value || 0);
  return new Intl.NumberFormat(localeFor(language), {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatNumber(value, language) {
  return new Intl.NumberFormat(localeFor(language), {
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
}

export function formatDate(value, language) {
  if (!value) return "-";
  return new Intl.DateTimeFormat(localeFor(language), {
    dateStyle: "medium",
    timeStyle: value.includes?.("T") ? "short" : undefined,
  }).format(new Date(value));
}

export function formatRelativeTime(value, language) {
  if (!value) return "-";
  const date = new Date(value);
  const diffSeconds = Math.round((date.getTime() - Date.now()) / 1000);
  const divisions = [
    { amount: 60, unit: "second" },
    { amount: 60, unit: "minute" },
    { amount: 24, unit: "hour" },
    { amount: 7, unit: "day" },
    { amount: 4.345, unit: "week" },
    { amount: 12, unit: "month" },
    { amount: Number.POSITIVE_INFINITY, unit: "year" },
  ];
  let duration = diffSeconds;
  for (const division of divisions) {
    if (Math.abs(duration) < division.amount) {
      return new Intl.RelativeTimeFormat(localeFor(language), { numeric: "auto" }).format(
        Math.round(duration),
        division.unit
      );
    }
    duration /= division.amount;
  }
  return formatDate(value, language);
}

export function titleFromKey(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}
