import CrudPage from "./CrudPage";
import { clientConfig } from "./resourceConfigs";
import { useLanguage } from "../context/LanguageContext";

export default function ClientsPage() {
  const { t } = useLanguage();
  return <CrudPage title={t("clients")} subtitle={t("page.clients.subtitle")} {...clientConfig} />;
}
