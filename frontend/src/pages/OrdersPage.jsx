import { useNavigate } from "react-router-dom";

import CrudPage from "./CrudPage";
import { orderConfig } from "./resourceConfigs";
import { useLanguage } from "../context/LanguageContext";

export default function OrdersPage() {
  const { t } = useLanguage();
  const navigate = useNavigate();
  return (
    <CrudPage
      title={t("orders")}
      subtitle={t("page.orders.subtitle")}
      {...orderConfig}
      onRowClick={(row) => navigate(`/orders/${row.id}`)}
    />
  );
}
