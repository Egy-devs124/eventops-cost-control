import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [username, setUsername] = useState("owner@example.com");
  const [password, setPassword] = useState("Admin12345");
  const [error, setError] = useState("");

  if (isAuthenticated) return <Navigate to="/" replace />;

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      await login(username, password);
      navigate("/");
    } catch {
      setError(t("message.invalidLogin"));
    }
  }

  return (
    <main className="login-page">
      <section className="login-panel">
        <div className="brand large">
          <span className="brand-mark">EO</span>
          <div>
            <strong>{t("appName")}</strong>
            <small>{t("app.tagline")}</small>
          </div>
        </div>
        <form onSubmit={submit}>
          <label className="form-field">
            <span>{t("username")}</span>
            <input value={username} onChange={(event) => setUsername(event.target.value)} />
          </label>
          <label className="form-field">
            <span>{t("password")}</span>
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
          </label>
          {error ? <div className="form-error">{error}</div> : null}
          <button className="button primary full" type="submit">
            {t("login")}
          </button>
        </form>
      </section>
    </main>
  );
}
