import { useState } from "react";

import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useLanguage } from "../context/LanguageContext";
import { formatDate } from "../utils/format";
import CrudPage from "./CrudPage";
import { staffConfig, statusOptions } from "./resourceConfigs";

const taskConfig = {
  endpoint: "/staff/tasks/",
  columns: [
    { key: "staff_name", labelKey: "field.staff" },
    { key: "order_code", labelKey: "field.order" },
    { key: "title", labelKey: "field.title" },
    { key: "status", labelKey: "field.status", render: (row) => <StatusBadge value={row.status} /> },
    { key: "due_at", labelKey: "field.due_at", render: (row) => formatDate(row.due_at) },
  ],
  fields: [
    { name: "staff", labelKey: "field.staff", type: "lookup", lookup: "/lookups/staff/", placeholderKey: "placeholder.selectStaff" },
    { name: "order", labelKey: "field.order", type: "lookup", lookup: "/lookups/orders/", placeholderKey: "placeholder.selectOrder", nullable: true },
    { name: "title", labelKey: "field.title" },
    { name: "status", labelKey: "field.status", type: "select", options: statusOptions.task },
    { name: "due_at", labelKey: "field.due_at", type: "datetime", nullable: true },
    { name: "notes", labelKey: "field.notes" },
  ],
  defaults: { status: "todo" },
};

export default function StaffPage() {
  const { t } = useLanguage();
  const [tab, setTab] = useState("staff");
  return (
    <>
      <PageHeader title={t("staff")} subtitle={t("page.staff.subtitle")} />
      <div className="tabs">
        <button className={tab === "staff" ? "active" : ""} onClick={() => setTab("staff")}>{t("staff")}</button>
        <button className={tab === "tasks" ? "active" : ""} onClick={() => setTab("tasks")}>{t("tasks")}</button>
      </div>
      <CrudPage title={tab === "staff" ? t("staff") : t("tasks")} {...(tab === "staff" ? staffConfig : taskConfig)} embedded />
    </>
  );
}
