import { useState } from "react";

import { api } from "../api/client";
import { FormInput } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { SelectInput } from "../components/SelectInput";
import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";
import { useTheme } from "../context/ThemeContext";

export default function ProfilePage() {
  const { user } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const { theme, setTheme } = useTheme();
  const [form, setForm] = useState(user || {});
  const [message, setMessage] = useState("");

  function setField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    await api.patch("/auth/me/", form);
    setLanguage(form.language || language);
    setTheme(form.theme || theme);
    setMessage(t("message.profileSaved"));
  }

  return (
    <>
      <PageHeader title={t("profile")} subtitle={t("page.profile.subtitle")} />
      <form className="settings-panel" onSubmit={submit}>
        <FormInput label={t("field.first_name")} name="first_name" value={form.first_name} onChange={setField} />
        <FormInput label={t("field.last_name")} name="last_name" value={form.last_name} onChange={setField} />
        <FormInput label={t("field.email")} name="email" value={form.email} onChange={setField} />
        <FormInput label={t("field.phone")} name="phone" value={form.phone} onChange={setField} />
        <SelectInput label={t("field.language")} name="language" value={form.language || language} onChange={setField} options={[{ value: "en", labelKey: "english" }, { value: "ar", labelKey: "arabic" }]} />
        <SelectInput label={t("field.theme")} name="theme" value={form.theme || theme} onChange={setField} options={[{ value: "light", labelKey: "light" }, { value: "dark", labelKey: "dark" }]} />
        {message ? <div className="notice">{message}</div> : null}
        <button className="button primary" type="submit">{t("save")}</button>
      </form>
    </>
  );
}
