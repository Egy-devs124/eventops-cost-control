import {
  AlertTriangle,
  Banknote,
  CalendarDays,
  CircleDollarSign,
  ClipboardCheck,
  FileText,
  HandCoins,
  ReceiptText,
  TrendingUp,
  Warehouse,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { api } from "../api/client";
import { AmountDisplay } from "../components/AmountDisplay";
import { ChartCard } from "../components/ChartCard";
import { DashboardCard } from "../components/DashboardCard";
import { PageHeader } from "../components/PageHeader";
import { useLanguage } from "../context/LanguageContext";
import { formatDate } from "../utils/format";

export default function DashboardPage() {
  const { language, t } = useLanguage();
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/reports/dashboard/").then((response) => setData(response.data));
  }, []);

  const statusData = data?.orders_by_status?.map((row) => ({
    name: t(`orderStatus.${row.status}`),
    count: row.count,
  })) || [];

  return (
    <>
      <PageHeader title={t("dashboard")} subtitle={t("page.dashboard.subtitle")} />
      <section className="dashboard-grid">
        <DashboardCard title={t("dashboard.ordersThisMonth")} value={data?.total_orders_this_month} icon={ClipboardCheck} />
        <DashboardCard title={t("dashboard.confirmedJobs")} value={data?.confirmed_jobs} icon={CalendarDays} tone="green" />
        <DashboardCard title={t("dashboard.pendingQuotations")} value={data?.pending_quotations} icon={FileText} tone="amber" />
        <DashboardCard title={t("todayJobs")} value={data?.todays_jobs} icon={CalendarDays} />
        <DashboardCard title={t("upcomingJobs")} value={data?.upcoming_jobs} icon={TrendingUp} />
        <DashboardCard title={t("revenue")} value={data?.total_revenue} amount icon={ReceiptText} tone="green" />
        <DashboardCard title={t("collected")} value={data?.total_collected} amount icon={HandCoins} />
        <DashboardCard title={t("outstanding")} value={data?.outstanding_client_balances} amount icon={AlertTriangle} tone="amber" />
        <DashboardCard title={t("vendorPayables")} value={data?.vendor_payables} amount icon={CircleDollarSign} />
        <DashboardCard title={t("driverPayables")} value={data?.driver_payables} amount icon={CircleDollarSign} />
        <DashboardCard title={t("payrollDue")} value={data?.payroll_due} amount icon={Banknote} tone="amber" />
        <DashboardCard title={t("cashboxBalance")} value={data?.cashbox_balance} amount icon={Banknote} tone="green" />
        <DashboardCard title={t("dashboard.netProfit")} value={data?.net_profit} amount icon={TrendingUp} tone="green" />
        <DashboardCard title={t("unavailableItems")} value={data?.items_unavailable} icon={Warehouse} tone="red" />
      </section>

      <section className="two-column">
        <ChartCard title={t("dashboard.jobsByStatus")}>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={statusData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" hide />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#0f9f8f" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title={t("lowProfitJobs")}>
          <div className="stack-list">
            {(data?.low_negative_profit_jobs || []).map((job) => (
              <div className="stack-row" key={job.order}>
                <div>
                  <strong>{job.code}</strong>
                  <span>{Number(job.margin_percent).toFixed(2)}%</span>
                </div>
                <AmountDisplay value={job.profit} />
              </div>
            ))}
            {!data?.low_negative_profit_jobs?.length ? <p className="muted">{t("dashboard.noWarnings")}</p> : null}
          </div>
        </ChartCard>
      </section>

      <section className="two-column">
        <ChartCard title={t("dashboard.recentPayments")}>
          <div className="stack-list">
            {(data?.recent_payments || []).map((payment) => (
              <div className="stack-row" key={payment.id}>
                <div>
                  <strong>{payment.client__name}</strong>
                  <span>{formatDate(payment.payment_date, language)}</span>
                </div>
                <AmountDisplay value={payment.amount} />
              </div>
            ))}
          </div>
        </ChartCard>
        <ChartCard title={t("dashboard.recentExpenses")}>
          <div className="stack-list">
            {(data?.recent_expenses || []).map((expense) => (
              <div className="stack-row" key={expense.id}>
                <div>
                  <strong>{expense.category__name}</strong>
                  <span>{expense.description}</span>
                </div>
                <AmountDisplay value={expense.amount} />
              </div>
            ))}
          </div>
        </ChartCard>
      </section>
    </>
  );
}
