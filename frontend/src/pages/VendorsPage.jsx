import CrudPage from "./CrudPage";
import { vendorConfig } from "./resourceConfigs";
import { useLanguage } from "../context/LanguageContext";

export default function VendorsPage() {
  const { t } = useLanguage();
  return <CrudPage title={t("vendors")} subtitle={t("page.vendors.subtitle")} {...vendorConfig} />;
}
