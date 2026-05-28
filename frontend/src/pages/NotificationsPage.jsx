import { api } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";
import { formatRelativeTime } from "../utils/format";
import CrudPage from "./CrudPage";
import { useLanguage } from "../context/LanguageContext";

export default function NotificationsPage() {
  const { language, t } = useLanguage();
  return (
    <CrudPage
      title={t("notifications")}
      endpoint="/notifications/"
      columns={[
        { key: "title", labelKey: "field.title" },
        { key: "message", labelKey: "field.message" },
        { key: "is_read", labelKey: "field.read", render: (row) => <StatusBadge value={row.is_read ? "read" : "unread"} /> },
        { key: "created_at", labelKey: "field.date", render: (row) => formatRelativeTime(row.created_at, language) },
      ]}
      fields={[
        { name: "title", labelKey: "field.title" },
        { name: "message", labelKey: "field.message" },
        { name: "user", labelKey: "field.user", type: "lookup", lookup: "/lookups/users/", placeholderKey: "placeholder.selectUser" },
      ]}
      onRowClick={(row) => api.post(`/notifications/${row.id}/mark-read/`)}
    />
  );
}
