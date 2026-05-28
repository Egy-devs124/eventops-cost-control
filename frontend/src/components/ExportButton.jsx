import { Download } from "lucide-react";

import { API_BASE_URL } from "../api/client";
import { useLanguage } from "../context/LanguageContext";

export function ExportButton({ report = "profit", format = "csv", labelKey = "action.export" }) {
  const { language, t } = useLanguage();
  function handleExport() {
    const token = localStorage.getItem("eventops.access");
    const url = `${API_BASE_URL}/reports/export/?report=${report}&file_format=${format}&lang=${language}`;
    fetch(url, { headers: { Authorization: `Bearer ${token}`, "Accept-Language": language } })
      .then((response) => response.blob())
      .then((blob) => {
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `${report}-report.${format}`;
        link.click();
        URL.revokeObjectURL(link.href);
      });
  }

  return (
    <button className="button secondary" type="button" onClick={handleExport}>
      <Download size={16} />
      {t(labelKey)}
    </button>
  );
}
