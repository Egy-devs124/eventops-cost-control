import { useState } from "react";

import { api } from "../api/client";
import { PageHeader } from "../components/PageHeader";
import { useLanguage } from "../context/LanguageContext";
import CrudPage from "./CrudPage";
import { quotationConfig } from "./resourceConfigs";

export default function QuotationsPage() {
  const { t } = useLanguage();
  const [message, setMessage] = useState("");

  async function convertLatest() {
    const list = await api.get("/quotations/");
    const first = list.data.results?.[0] || list.data[0];
    if (!first) return setMessage(t("message.noQuotations"));
    const response = await api.post(`/quotations/${first.id}/convert-to-order/`);
    setMessage(t("message.convertedQuotation", undefined, { from: first.code, to: response.data.code }));
  }

  return (
    <>
      <PageHeader
        title={t("quotations")}
        subtitle={t("page.quotations.subtitle")}
        actions={<button className="button secondary" onClick={convertLatest}>{t("action.convertLatest")}</button>}
      />
      {message ? <div className="notice">{message}</div> : null}
      <CrudPage title={t("quotations")} {...quotationConfig} embedded />
    </>
  );
}
