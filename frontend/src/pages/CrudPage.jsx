import { Plus } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { createResource, deleteResource, fetchResource, updateResource } from "../api/resources";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { DataTable } from "../components/DataTable";
import { DatePicker } from "../components/DatePicker";
import { FormInput } from "../components/FormInput";
import { PageHeader } from "../components/PageHeader";
import { AsyncSearchableSelect } from "../components/SearchableSelect";
import { SelectInput } from "../components/SelectInput";
import { useLanguage } from "../context/LanguageContext";
import { listFromResponse } from "../api/client";
import { formatApiError } from "../utils/errors";

function cleanPayload(payload, fields) {
  return fields.reduce((acc, field) => {
    if (field.readOnly) return acc;
    let value = payload[field.name];
    if (value === "") value = field.nullable ? null : "";
    if (field.type === "number" && value !== "" && value !== null) value = Number(value);
    if (field.type === "lookup" && value !== "" && value !== null) value = Number(value);
    acc[field.name] = value;
    return acc;
  }, {});
}

export default function CrudPage({
  title,
  subtitle,
  endpoint,
  columns,
  fields,
  defaults = {},
  embedded = false,
  createLabel,
  onRowClick,
}) {
  const { t } = useLanguage();
  const [rows, setRows] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(defaults);
  const [error, setError] = useState("");
  const [deleteTarget, setDeleteTarget] = useState(null);

  const editableFields = useMemo(() => fields.filter((field) => !field.readOnly), [fields]);

  async function load() {
    setLoading(true);
    try {
      const response = await fetchResource(endpoint, search ? { search } : {});
      setRows(listFromResponse(response.data));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const timer = setTimeout(load, 250);
    return () => clearTimeout(timer);
  }, [endpoint, search]);

  function openCreate() {
    setError("");
    setEditing({ id: null });
    setForm(defaults);
  }

  function openEdit(row) {
    setError("");
    setEditing(row);
    setForm(row);
  }

  function setField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    setError("");
    const payload = cleanPayload(form, editableFields);
    try {
      if (editing?.id) {
        await updateResource(endpoint, editing.id, payload);
      } else {
        await createResource(endpoint, payload);
      }
      setEditing(null);
      await load();
    } catch (err) {
      setError(formatApiError(err.response?.data || { detail: err.message }, t));
    }
  }

  async function confirmDelete() {
    await deleteResource(endpoint, deleteTarget.id);
    setDeleteTarget(null);
    await load();
  }

  const header = (
    <PageHeader
      title={title}
      subtitle={subtitle}
      actions={
        <button className="button primary" type="button" onClick={openCreate}>
          <Plus size={16} />
          {createLabel || t("create")}
        </button>
      }
    />
  );

  return (
    <>
      {embedded ? null : header}
      {embedded ? (
        <div className="embedded-header">
          <h2>{title}</h2>
          <button className="button primary" type="button" onClick={openCreate}>
            <Plus size={16} />
            {createLabel || t("create")}
          </button>
        </div>
      ) : null}
      <DataTable
        columns={columns}
        rows={rows}
        loading={loading}
        search={search}
        onSearch={setSearch}
        onEdit={openEdit}
        onDelete={setDeleteTarget}
        onRowClick={onRowClick}
      />
      {editing ? (
        <div className="modal-backdrop">
          <form className="modal" onSubmit={submit}>
            <h2>{editing.id ? t("edit") : t("create")} {title}</h2>
            <div className="form-grid">
              {editableFields.map((field) => {
                const label = t(field.labelKey || `field.${field.name}`, field.label);
                const placeholder = t(field.placeholderKey, field.placeholder);
                if (field.type === "select") {
                  return (
                    <SelectInput
                      key={field.name}
                      label={label}
                      name={field.name}
                      value={form[field.name]}
                      onChange={setField}
                      options={field.options}
                    />
                  );
                }
                if (field.type === "lookup") {
                  return (
                    <AsyncSearchableSelect
                      key={field.name}
                      label={label}
                      value={form[field.name]}
                      onChange={(value) => setField(field.name, value)}
                      endpoint={field.lookup}
                      placeholder={field.placeholderKey || placeholder}
                    />
                  );
                }
                if (field.type === "date" || field.type === "datetime") {
                  return (
                    <DatePicker
                      key={field.name}
                      label={label}
                      name={field.name}
                      value={String(form[field.name] || "").slice(0, field.type === "datetime" ? 16 : 10)}
                      onChange={setField}
                      withTime={field.type === "datetime"}
                    />
                  );
                }
                return (
                  <FormInput
                    key={field.name}
                    label={label}
                    name={field.name}
                    value={form[field.name]}
                    onChange={setField}
                    type={field.type || "text"}
                  />
                );
              })}
            </div>
            {error ? <pre className="form-error">{error}</pre> : null}
            <div className="modal-actions">
              <button className="button ghost" type="button" onClick={() => setEditing(null)}>
                {t("cancel")}
              </button>
              <button className="button primary" type="submit">
                {t("save")}
              </button>
            </div>
          </form>
        </div>
      ) : null}
      <ConfirmDialog
        open={Boolean(deleteTarget)}
        title={t("delete")}
        message={t("message.deleteConfirm")}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={confirmDelete}
      />
    </>
  );
}
