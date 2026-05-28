import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { AmountDisplay } from "../components/AmountDisplay";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useLanguage } from "../context/LanguageContext";
import { formatDate } from "../utils/format";
import CrudPage from "./CrudPage";
import { statusOptions } from "./resourceConfigs";

const configs = {
  payments: {
    endpoint: "/finance/payments/",
    columns: [
      { key: "client_name", labelKey: "field.client" },
      { key: "invoice_code", labelKey: "field.invoice" },
      { key: "payment_date", labelKey: "field.date", render: (row) => formatDate(row.payment_date) },
      { key: "amount", labelKey: "field.amount", render: (row) => <AmountDisplay value={row.amount} /> },
      { key: "reference", labelKey: "field.reference" },
    ],
    fields: [
      { name: "client", labelKey: "field.client", type: "lookup", lookup: "/lookups/clients/", placeholderKey: "placeholder.selectClient" },
      { name: "order", labelKey: "field.order", type: "lookup", lookup: "/lookups/orders/", placeholderKey: "placeholder.selectOrder", nullable: true },
      { name: "invoice", labelKey: "field.invoice", type: "lookup", lookup: "/lookups/invoices/", placeholderKey: "placeholder.selectInvoice", nullable: true },
      { name: "amount", labelKey: "field.amount", type: "number" },
      { name: "payment_date", labelKey: "field.payment_date", type: "date" },
      { name: "method", labelKey: "field.method", type: "lookup", lookup: "/lookups/payment-methods/", placeholderKey: "placeholder.selectMethod", nullable: true },
      { name: "cashbox", labelKey: "field.cashbox", type: "lookup", lookup: "/lookups/cashboxes/", placeholderKey: "placeholder.selectCashbox", nullable: true },
      { name: "reference", labelKey: "field.reference" },
      { name: "notes", labelKey: "field.notes" },
    ],
    defaults: { amount: 0 },
  },
  expenses: {
    endpoint: "/finance/expenses/",
    columns: [
      { key: "category_name", labelKey: "field.category" },
      { key: "order_code", labelKey: "field.order" },
      { key: "expense_date", labelKey: "field.date", render: (row) => formatDate(row.expense_date) },
      { key: "amount", labelKey: "field.amount", render: (row) => <AmountDisplay value={row.amount} /> },
      { key: "status", labelKey: "field.status", render: (row) => <StatusBadge value={row.status} namespace="invoiceStatus" /> },
    ],
    fields: [
      { name: "category", labelKey: "field.category", type: "lookup", lookup: "/lookups/expense-categories/", placeholderKey: "placeholder.selectCategory" },
      { name: "order", labelKey: "field.order", type: "lookup", lookup: "/lookups/orders/", placeholderKey: "placeholder.selectOrder", nullable: true },
      { name: "amount", labelKey: "field.amount", type: "number" },
      { name: "expense_date", labelKey: "field.expense_date", type: "date" },
      { name: "description", labelKey: "field.description" },
      { name: "vendor", labelKey: "field.vendor", type: "lookup", lookup: "/lookups/vendors/", placeholderKey: "placeholder.selectVendor", nullable: true },
    ],
    defaults: { amount: 0 },
  },
  invoices: {
    endpoint: "/finance/invoices/",
    columns: [
      { key: "code", labelKey: "field.code" },
      { key: "client_name", labelKey: "field.client" },
      { key: "status", labelKey: "field.status", render: (row) => <StatusBadge value={row.status} /> },
      { key: "total_amount", labelKey: "field.total_amount", render: (row) => <AmountDisplay value={row.total_amount} /> },
      { key: "balance", labelKey: "field.balance", render: (row) => <AmountDisplay value={row.balance} /> },
    ],
    fields: [
      { name: "client", labelKey: "field.client", type: "lookup", lookup: "/lookups/clients/", placeholderKey: "placeholder.selectClient" },
      { name: "order", labelKey: "field.order", type: "lookup", lookup: "/lookups/orders/", placeholderKey: "placeholder.selectOrder", nullable: true },
      { name: "issue_date", labelKey: "field.issue_date", type: "date" },
      { name: "due_date", labelKey: "field.due_date", type: "date", nullable: true },
      { name: "status", labelKey: "field.status", type: "select", options: statusOptions.invoice },
      { name: "subtotal", labelKey: "field.subtotal", type: "number" },
      { name: "discount_amount", labelKey: "field.discount_amount", type: "number" },
      { name: "tax_amount", labelKey: "field.tax_amount", type: "number" },
      { name: "total_amount", labelKey: "field.total_amount", type: "number" },
      { name: "notes", labelKey: "field.notes" },
    ],
    defaults: { status: "draft", subtotal: 0, discount_amount: 0, tax_amount: 0, total_amount: 0 },
  },
  cashboxes: {
    endpoint: "/finance/cashboxes/",
    columns: [
      { key: "name", labelKey: "field.name" },
      { key: "currency", labelKey: "field.currency" },
      { key: "opening_balance", labelKey: "field.opening", render: (row) => <AmountDisplay value={row.opening_balance} /> },
      { key: "balance", labelKey: "field.balance", render: (row) => <AmountDisplay value={row.balance} /> },
    ],
    fields: [
      { name: "name", labelKey: "field.name" },
      { name: "opening_balance", labelKey: "field.opening_balance", type: "number" },
      { name: "currency", labelKey: "field.currency" },
      { name: "notes", labelKey: "field.notes" },
    ],
    defaults: { opening_balance: 0, currency: "EGP" },
  },
};

export default function FinancePage() {
  const { t } = useLanguage();
  const [params] = useSearchParams();
  const [tab, setTab] = useState(params.get("tab") || "payments");
  const tabs = useMemo(() => ["payments", "expenses", "invoices", "cashboxes"], []);
  return (
    <>
      <PageHeader title={t("finance")} subtitle={t("page.finance.subtitle")} />
      <div className="tabs">
        {tabs.map((key) => (
          <button key={key} className={tab === key ? "active" : ""} onClick={() => setTab(key)}>
            {t(key)}
          </button>
        ))}
      </div>
      <CrudPage title={t(tab)} {...configs[tab]} embedded />
    </>
  );
}
