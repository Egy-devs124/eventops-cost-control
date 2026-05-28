import { PageHeader } from "../components/PageHeader";
import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";

export default function SettingsPage() {
  const { user, permissions } = useAuth();
  const { t } = useLanguage();

  return (
    <>
      <PageHeader title={t("settings")} subtitle={t("page.settings.subtitle")} />
      <section className="settings-panel">
        <h2>{t("message.currentAccess")}</h2>
        <div className="detail-grid">
          <div className="detail-panel"><span>{t("field.user")}</span><strong>{user?.username}</strong></div>
          <div className="detail-panel"><span>{t("field.role")}</span><strong>{user?.role_name}</strong></div>
          <div className="detail-panel"><span>{t("field.profitReports")}</span><strong>{permissions?.can_view_profit ? t("message.allowed") : t("message.restricted")}</strong></div>
          <div className="detail-panel"><span>{t("field.payroll")}</span><strong>{permissions?.can_view_payroll ? t("message.allowed") : t("message.restricted")}</strong></div>
        </div>
      </section>
    </>
  );
}
