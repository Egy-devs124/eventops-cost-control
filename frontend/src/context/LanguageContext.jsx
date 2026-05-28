import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { translations } from "../i18n/translations";

const LanguageContext = createContext(null);
const RTL_LANGUAGES = new Set(["ar"]);

function interpolate(value, params) {
  if (!params || typeof value !== "string") return value;
  return Object.entries(params).reduce(
    (text, [key, replacement]) => text.replaceAll(`{${key}}`, replacement ?? ""),
    value
  );
}

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(
    localStorage.getItem("eventops.language") || "en"
  );

  useEffect(() => {
    localStorage.setItem("eventops.language", language);
    document.documentElement.lang = language;
    document.documentElement.dir = RTL_LANGUAGES.has(language) ? "rtl" : "ltr";
  }, [language]);

  const value = useMemo(
    () => ({
      language,
      direction: RTL_LANGUAGES.has(language) ? "rtl" : "ltr",
      setLanguage,
      t: (key, fallback, params) =>
        interpolate(
          translations[language]?.[key] ?? translations.en?.[key] ?? fallback ?? key,
          params
        ),
    }),
    [language]
  );

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
