import { X } from "lucide-react";

import { useLanguage } from "../context/LanguageContext";

export function ConfirmDialog({ open, title, message, confirmLabel, onConfirm, onCancel }) {
  const { t } = useLanguage();
  if (!open) return null;
  return (
    <div className="modal-backdrop" role="presentation">
      <section className="modal compact" role="dialog" aria-modal="true">
        <button className="icon-button close-button" type="button" onClick={onCancel} aria-label={t("action.closeDialog")}>
          <X size={18} />
        </button>
        <h2>{title}</h2>
        <p>{message}</p>
        <div className="modal-actions">
          <button className="button ghost" type="button" onClick={onCancel}>
            {t("action.cancel")}
          </button>
          <button className="button danger" type="button" onClick={onConfirm}>
            {confirmLabel || t("action.delete")}
          </button>
        </div>
      </section>
    </div>
  );
}
