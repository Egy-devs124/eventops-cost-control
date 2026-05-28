export function FormInput({ label, name, value, onChange, type = "text", required = false, ...props }) {
  return (
    <label className="form-field">
      <span>{label}</span>
      <input
        name={name}
        value={value ?? ""}
        onChange={(event) => onChange(name, event.target.value)}
        type={type}
        required={required}
        {...props}
      />
    </label>
  );
}
