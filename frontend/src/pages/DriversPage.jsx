import { useState } from "react";

import { AmountDisplay } from "../components/AmountDisplay";
import { StatusBadge } from "../components/StatusBadge";
import { PageHeader } from "../components/PageHeader";
import { useLanguage } from "../context/LanguageContext";
import { formatDate } from "../utils/format";
import CrudPage from "./CrudPage";
import { driverConfig, statusOptions } from "./resourceConfigs";

const tripsConfig = {
  endpoint: "/drivers/trips/",
  columns: [
    { key: "driver_name", labelKey: "field.driver" },
    { key: "order_code", labelKey: "field.order" },
    { key: "scheduled_at", labelKey: "field.scheduled_at", render: (row) => formatDate(row.scheduled_at) },
    { key: "status", labelKey: "field.status", render: (row) => <StatusBadge value={row.status} /> },
    { key: "cost", labelKey: "field.cost", render: (row) => <AmountDisplay value={row.cost} /> },
  ],
  fields: [
    { name: "driver", labelKey: "field.driver", type: "lookup", lookup: "/lookups/drivers/", placeholderKey: "placeholder.selectDriver" },
    { name: "order", labelKey: "field.order", type: "lookup", lookup: "/lookups/orders/", placeholderKey: "placeholder.selectOrder", nullable: true },
    { name: "pickup_location", labelKey: "field.pickup_location" },
    { name: "dropoff_location", labelKey: "field.dropoff_location" },
    { name: "scheduled_at", labelKey: "field.scheduled_at", type: "datetime" },
    { name: "status", labelKey: "field.status", type: "select", options: statusOptions.trip },
    { name: "cost", labelKey: "field.cost", type: "number" },
    { name: "notes", labelKey: "field.notes" },
  ],
  defaults: { status: "scheduled", cost: 0 },
};

export default function DriversPage() {
  const { t } = useLanguage();
  const [tab, setTab] = useState("drivers");
  return (
    <>
      <PageHeader title={t("drivers")} subtitle={t("page.drivers.subtitle")} />
      <div className="tabs">
        <button className={tab === "drivers" ? "active" : ""} onClick={() => setTab("drivers")}>{t("drivers")}</button>
        <button className={tab === "trips" ? "active" : ""} onClick={() => setTab("trips")}>{t("trips")}</button>
      </div>
      <CrudPage title={tab === "drivers" ? t("drivers") : t("trips")} {...(tab === "drivers" ? driverConfig : tripsConfig)} embedded />
    </>
  );
}
