import { AmountDisplay } from "../components/AmountDisplay";
import { StatusBadge } from "../components/StatusBadge";
import { useLanguage } from "../context/LanguageContext";
import { formatDate } from "../utils/format";
import CrudPage from "./CrudPage";
import { statusOptions } from "./resourceConfigs";

export default function PayrollPage() {
  const { t } = useLanguage();
  return (
    <CrudPage
      title={t("payroll")}
      subtitle={t("page.payroll.subtitle")}
      endpoint="/payroll/"
      columns={[
        { key: "name", labelKey: "field.name" },
        { key: "start_date", labelKey: "field.start_date", render: (row) => formatDate(row.start_date) },
        { key: "end_date", labelKey: "field.end_date", render: (row) => formatDate(row.end_date) },
        { key: "status", labelKey: "field.status", render: (row) => <StatusBadge value={row.status} namespace="payrollStatus" /> },
        { key: "lines", labelKey: "field.lines", render: (row) => row.lines?.length || 0 },
      ]}
      fields={[
        { name: "name", labelKey: "field.name" },
        { name: "start_date", labelKey: "field.start_date", type: "date" },
        { name: "end_date", labelKey: "field.end_date", type: "date" },
        { name: "status", labelKey: "field.status", type: "select", options: statusOptions.payroll },
      ]}
      defaults={{ status: "draft" }}
    />
  );
}
