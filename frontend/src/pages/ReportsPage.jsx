import { Printer } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "../api/client";
import { AmountDisplay } from "../components/AmountDisplay";
import { DataTable } from "../components/DataTable";
import { ExportButton } from "../components/ExportButton";
import { PageHeader } from "../components/PageHeader";
import { useLanguage } from "../context/LanguageContext";

export default function ReportsPage() {
  const { t } = useLanguage();
  const [profit, setProfit] = useState([]);
  const [clients, setClients] = useState([]);
  const [vendors, setVendors] = useState([]);

  useEffect(() => {
    Promise.allSettled([
      api.get("/reports/profit/"),
      api.get("/reports/client-balances/"),
      api.get("/reports/vendor-balances/"),
    ]).then(([profitRes, clientRes, vendorRes]) => {
      if (profitRes.status === "fulfilled") setProfit(profitRes.value.data);
      if (clientRes.status === "fulfilled") setClients(clientRes.value.data);
      if (vendorRes.status === "fulfilled") setVendors(vendorRes.value.data);
    });
  }, []);

  return (
    <>
      <PageHeader
        title={t("reports")}
        subtitle={t("page.reports.subtitle")}
        actions={
          <>
            <ExportButton report="profit" format="csv" labelKey="action.downloadCsv" />
            <ExportButton report="profit" format="xlsx" labelKey="action.downloadExcel" />
            <button className="button secondary" type="button" onClick={() => window.print()}>
              <Printer size={16} />
              {t("action.print")}
            </button>
          </>
        }
      />
      <section className="two-column">
        <div>
          <h2>{t("reports.profitByJob")}</h2>
          <DataTable
            rows={profit}
            columns={[
              { key: "order_number", labelKey: "field.order" },
              { key: "client", labelKey: "field.client" },
              { key: "revenue", labelKey: "revenue", render: (row) => <AmountDisplay value={row.revenue} /> },
              { key: "total_costs", labelKey: "field.total_costs", render: (row) => <AmountDisplay value={row.total_costs} /> },
              { key: "profit", labelKey: "profit", render: (row) => <AmountDisplay value={row.profit} /> },
              { key: "margin_percent", labelKey: "field.margin_percent" },
            ]}
          />
        </div>
        <div>
          <h2>{t("reports.clientReceivables")}</h2>
          <DataTable
            rows={clients}
            columns={[
              { key: "name", labelKey: "field.client" },
              { key: "balance", labelKey: "field.balance", render: (row) => <AmountDisplay value={row.balance} /> },
            ]}
          />
        </div>
      </section>
      <section>
        <h2>{t("reports.vendorPayables")}</h2>
        <DataTable
          rows={vendors}
          columns={[
            { key: "name", labelKey: "field.vendor" },
            { key: "balance", labelKey: "field.balance", render: (row) => <AmountDisplay value={row.balance} /> },
          ]}
        />
      </section>
    </>
  );
}
