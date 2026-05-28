import { CheckCircle2, Lock, PackageCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { api, listFromResponse } from "../api/client";
import { AmountDisplay } from "../components/AmountDisplay";
import { DataTable } from "../components/DataTable";
import { PageHeader } from "../components/PageHeader";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";
import { formatApiError } from "../utils/errors";
import { formatDate, formatNumber } from "../utils/format";

const tabs = ["overview", "items", "costs", "payments", "staff", "vendors", "drivers", "attachments", "timeline", "profitability"];

export default function OrderDetailsPage() {
  const { id } = useParams();
  const { language, t } = useLanguage();
  const { permissions } = useAuth();
  const [order, setOrder] = useState(null);
  const [tab, setTab] = useState("overview");
  const [related, setRelated] = useState({});
  const [message, setMessage] = useState("");

  async function load() {
    const response = await api.get(`/orders/${id}/`);
    setOrder(response.data);
  }

  useEffect(() => {
    load();
  }, [id]);

  useEffect(() => {
    const endpoints = {
      items: `/orders/items/?order=${id}`,
      payments: `/finance/payments/?order=${id}`,
      costs: `/finance/expenses/?order=${id}`,
      staff: `/orders/staff-assignments/?order=${id}`,
      vendors: `/orders/vendor-assignments/?order=${id}`,
      drivers: `/orders/driver-assignments/?order=${id}`,
      timeline: `/orders/status-history/?order=${id}`,
    };
    const endpoint = endpoints[tab];
    if (!endpoint) return;
    api.get(endpoint).then((response) => setRelated((current) => ({ ...current, [tab]: listFromResponse(response.data) })));
  }, [tab, id]);

  async function action(path, success) {
    setMessage("");
    try {
      await api.post(`/orders/${id}/${path}/`);
      await load();
      setMessage(success);
    } catch (err) {
      setMessage(formatApiError(err.response?.data || { detail: err.message }, t));
    }
  }

  if (!order) return <div className="boot-loader">{t("loading")}...</div>;

  const profitability = order.profitability;

  return (
    <>
      <PageHeader
        title={`${order.code} · ${order.title}`}
        subtitle={`${order.client_name} · ${formatDate(order.start_at, language)} - ${formatDate(order.end_at, language)}`}
        actions={
          <>
            <button className="button secondary" type="button" onClick={() => action("confirm", t("message.orderConfirmed"))}>
              <PackageCheck size={16} />
              {t("action.confirm")}
            </button>
            <button className="button primary" type="button" onClick={() => action("close", t("message.orderClosed"))}>
              <CheckCircle2 size={16} />
              {t("action.close")}
            </button>
          </>
        }
      />
      {message ? <div className="notice">{message}</div> : null}
      <div className="tabs">
        {tabs
          .filter((key) => key !== "profitability" || permissions?.can_view_profit)
          .map((key) => (
            <button key={key} className={tab === key ? "active" : ""} onClick={() => setTab(key)}>
              {t(key)}
            </button>
          ))}
      </div>

      {tab === "overview" ? (
        <section className="detail-grid">
          <div className="detail-panel">
            <span>{t("field.status")}</span>
            <StatusBadge value={order.status} namespace="orderStatus" />
          </div>
          <div className="detail-panel">
            <span>{t("field.total_amount")}</span>
            <AmountDisplay value={order.total_amount} />
          </div>
          <div className="detail-panel">
            <span>{t("field.payment_status")}</span>
            <StatusBadge value={order.payment_status} namespace="paymentStatus" />
          </div>
          <div className="detail-panel wide">
            <span>{t("field.location")}</span>
            <strong>{order.event_location || "-"}</strong>
          </div>
          <div className="detail-panel wide">
            <span>{t("field.notes")}</span>
            <p>{order.notes || "-"}</p>
          </div>
        </section>
      ) : null}

      {tab === "items" ? (
        <DataTable
          rows={related.items || order.items || []}
          columns={[
            { key: "item_name", labelKey: "field.item" },
            { key: "quantity", labelKey: "field.qty" },
            { key: "unit_price", labelKey: "field.unit_price", render: (row) => <AmountDisplay value={row.unit_price} /> },
            { key: "cost_price", labelKey: "field.cost_price", render: (row) => <AmountDisplay value={row.cost_price} /> },
          ]}
        />
      ) : null}

      {tab === "costs" ? (
        <DataTable
          rows={related.costs || []}
          columns={[
            { key: "category_name", labelKey: "field.category" },
            { key: "description", labelKey: "field.description" },
            { key: "amount", labelKey: "field.amount", render: (row) => <AmountDisplay value={row.amount} /> },
            { key: "status", labelKey: "field.status", render: (row) => <StatusBadge value={row.status} /> },
          ]}
        />
      ) : null}

      {tab === "payments" ? (
        <DataTable
          rows={related.payments || []}
          columns={[
            { key: "payment_date", labelKey: "field.date", render: (row) => formatDate(row.payment_date, language) },
            { key: "amount", labelKey: "field.amount", render: (row) => <AmountDisplay value={row.amount} /> },
            { key: "reference", labelKey: "field.reference" },
          ]}
        />
      ) : null}

      {["staff", "vendors", "drivers"].includes(tab) ? (
        <DataTable
          rows={related[tab] || []}
          columns={[
            { key: tab === "staff" ? "staff_name" : tab === "vendors" ? "vendor_name" : "driver_name", labelKey: `field.${tab === "staff" ? "staff" : tab === "vendors" ? "vendor" : "driver"}` },
            { key: "status", labelKey: "field.status", render: (row) => <StatusBadge value={row.status} /> },
            { key: "cost", labelKey: "field.cost", render: (row) => <AmountDisplay value={row.cost} /> },
          ]}
        />
      ) : null}

      {tab === "timeline" ? (
        <DataTable
          rows={related.timeline || order.status_history || []}
          columns={[
            { key: "from_status", labelKey: "field.from_status", render: (row) => row.from_status ? <StatusBadge value={row.from_status} namespace="orderStatus" /> : "-" },
            { key: "to_status", labelKey: "field.to_status", render: (row) => <StatusBadge value={row.to_status} namespace="orderStatus" /> },
            { key: "changed_by_name", labelKey: "field.user" },
            { key: "created_at", labelKey: "field.date", render: (row) => formatDate(row.created_at, language) },
          ]}
        />
      ) : null}

      {tab === "attachments" ? (
        <section className="empty-panel">
          <Lock size={18} />
          {t("message.attachmentsHint")}
        </section>
      ) : null}

      {tab === "profitability" ? (
        <section className="detail-grid">
          {profitability ? (
            Object.entries(profitability)
              .filter(([key]) => !["order", "code", "warning"].includes(key))
              .map(([key, value]) => (
                <div className="detail-panel" key={key}>
                  <span>{t(`field.${key}`)}</span>
                  {key.includes("percent") ? <strong>{formatNumber(value, language)}%</strong> : <AmountDisplay value={value} />}
                </div>
              ))
          ) : (
            <div className="empty-panel">{t("message.profitabilityRestricted")}</div>
          )}
        </section>
      ) : null}
    </>
  );
}
