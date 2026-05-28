import { useState } from "react";

import CrudPage from "./CrudPage";
import { itemConfig } from "./resourceConfigs";
import { PageHeader } from "../components/PageHeader";
import { useLanguage } from "../context/LanguageContext";
import { statusOptions } from "./resourceConfigs";

const categoryConfig = {
  endpoint: "/items/categories/",
  columns: [
    { key: "name", labelKey: "field.name" },
    { key: "notes", labelKey: "field.notes" },
  ],
  fields: [
    { name: "name", labelKey: "field.name" },
    { name: "parent", labelKey: "field.parent", type: "lookup", lookup: "/lookups/item-categories/", placeholderKey: "placeholder.selectParentCategory", nullable: true },
    { name: "notes", labelKey: "field.notes" },
  ],
};

const transactionConfig = {
  endpoint: "/items/transactions/",
  columns: [
    { key: "item_name", labelKey: "field.item" },
    { key: "transaction_type", labelKey: "field.transaction_type" },
    { key: "quantity", labelKey: "field.qty" },
    { key: "reference", labelKey: "field.reference" },
  ],
  fields: [
    { name: "item", labelKey: "field.item", type: "lookup", lookup: "/lookups/items/", placeholderKey: "placeholder.selectItem" },
    { name: "transaction_type", labelKey: "field.transaction_type", type: "select", options: statusOptions.transaction },
    { name: "quantity", labelKey: "field.quantity", type: "number" },
    { name: "order", labelKey: "field.order", type: "lookup", lookup: "/lookups/orders/", placeholderKey: "placeholder.selectOrder", nullable: true },
    { name: "reference", labelKey: "field.reference" },
    { name: "notes", labelKey: "field.notes" },
  ],
  defaults: { transaction_type: "in", quantity: 1 },
};

export default function InventoryPage() {
  const { t } = useLanguage();
  const [tab, setTab] = useState("items");
  const tabs = [
    ["items", t("items")],
    ["categories", t("categories")],
    ["transactions", t("transactions")],
  ];
  const config = tab === "categories" ? categoryConfig : tab === "transactions" ? transactionConfig : itemConfig;

  return (
    <>
      <PageHeader title={t("inventory")} subtitle={t("page.inventory.subtitle")} />
      <div className="tabs">
        {tabs.map(([key, label]) => (
          <button key={key} className={tab === key ? "active" : ""} onClick={() => setTab(key)}>{label}</button>
        ))}
      </div>
      <CrudPage title={tabs.find(([key]) => key === tab)?.[1]} {...config} embedded />
    </>
  );
}
