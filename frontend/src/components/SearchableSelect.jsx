import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { api } from "../api/client";
import { useLanguage } from "../context/LanguageContext";

export function SearchableSelect({
  label,
  value,
  onChange,
  options = [],
  placeholder = "Search...",
  error,
  disabled = false,
}) {
  const { t } = useLanguage();
  const [query, setQuery] = useState("");
  const selected = useMemo(
    () => options.find((option) => String(option.value) === String(value)),
    [options, value]
  );
  const visibleOptions = options.filter((option) =>
    option.label.toLocaleLowerCase().includes(query.toLocaleLowerCase())
  );
  const placeholderText = t(placeholder, placeholder);

  return (
    <label className="form-field searchable-field">
      <span>{label}</span>
      <div className="select-search">
        <Search size={15} />
        <input
          value={query || selected?.label || ""}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={placeholderText}
          disabled={disabled}
        />
      </div>
      <select
        value={value ?? ""}
        onChange={(event) => onChange(event.target.value || null)}
        disabled={disabled}
      >
        <option value="">{placeholderText}</option>
        {visibleOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error ? <small className="field-error">{error}</small> : null}
    </label>
  );
}

export function AsyncSearchableSelect({
  label,
  value,
  onChange,
  endpoint,
  placeholder = "Search...",
  error,
  disabled,
}) {
  const { t } = useLanguage();
  const [options, setOptions] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => {
      api
        .get(endpoint, search ? { params: { search } } : {})
        .then((response) => setOptions(response.data))
        .catch(() => setOptions([]));
    }, 180);
    return () => clearTimeout(timer);
  }, [endpoint, search]);

  const selected = options.find((option) => String(option.value) === String(value));
  const placeholderText = t(placeholder, placeholder);

  return (
    <label className="form-field searchable-field">
      <span>{label}</span>
      <div className="select-search">
        <Search size={15} />
        <input
          value={search || selected?.label || ""}
          onChange={(event) => setSearch(event.target.value)}
          placeholder={placeholderText}
          disabled={disabled}
        />
      </div>
      <select
        value={value ?? ""}
        onChange={(event) => onChange(event.target.value || null)}
        disabled={disabled}
      >
        <option value="">{placeholderText}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error ? <small className="field-error">{error}</small> : null}
    </label>
  );
}
