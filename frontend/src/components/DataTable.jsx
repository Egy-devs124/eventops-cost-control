import { Edit, Search, Trash2 } from "lucide-react";

import { useLanguage } from "../context/LanguageContext";
import { titleFromKey } from "../utils/format";

export function DataTable({
  columns,
  rows,
  loading,
  search,
  onSearch,
  onEdit,
  onDelete,
  onRowClick,
}) {
  const { t } = useLanguage();
  const actionColumnCount = onEdit || onDelete ? 1 : 0;

  return (
    <section className="table-shell">
      {onSearch ? (
        <div className="table-toolbar">
          <label className="search-box">
            <Search size={16} />
            <input
              value={search}
              onChange={(event) => onSearch(event.target.value)}
              placeholder={t("search")}
            />
          </label>
        </div>
      ) : null}
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column.key}>{t(column.labelKey || `field.${column.key}`, column.label || titleFromKey(column.key))}</th>
              ))}
              {(onEdit || onDelete) && <th>{t("actions")}</th>}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={columns.length + actionColumnCount}>{t("loading")}...</td>
              </tr>
            ) : rows.length ? (
              rows.map((row) => (
                <tr key={row.id} onClick={() => onRowClick?.(row)}>
                  {columns.map((column) => (
                    <td key={column.key}>{column.render ? column.render(row) : row[column.key] ?? "-"}</td>
                  ))}
                  {(onEdit || onDelete) && (
                    <td className="row-actions" onClick={(event) => event.stopPropagation()}>
                      {onEdit ? (
                        <button className="icon-button" type="button" onClick={() => onEdit(row)} title={t("edit")}>
                          <Edit size={16} />
                        </button>
                      ) : null}
                      {onDelete ? (
                        <button className="icon-button danger" type="button" onClick={() => onDelete(row)} title={t("delete")}>
                          <Trash2 size={16} />
                        </button>
                      ) : null}
                    </td>
                  )}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length + actionColumnCount}>{t("noData")}</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
