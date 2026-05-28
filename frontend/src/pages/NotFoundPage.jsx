import { Link } from "react-router-dom";

import { useLanguage } from "../context/LanguageContext";

export default function NotFoundPage() {
  const { t } = useLanguage();
  return (
    <main className="empty-state">
      <h1>{t("message.pageNotFound")}</h1>
      <Link className="button primary" to="/">{t("action.backToDashboard")}</Link>
    </main>
  );
}
