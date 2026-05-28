import { useLanguage } from "../context/LanguageContext";

export function SelectInput({ label, name, value, onChange, options = [] }) {
  const { t } = useLanguage();
  return (
    <label className="form-field">
      <span>{label}</span>
      <select name={name} value={value ?? ""} onChange={(event) => onChange(name, event.target.value)}>
        <option value="">-</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {t(option.labelKey, option.label ?? option.value)}
          </option>
        ))}
      </select>
    </label>
  );
}
