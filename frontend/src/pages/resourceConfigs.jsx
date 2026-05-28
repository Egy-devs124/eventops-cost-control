import { AmountDisplay } from "../components/AmountDisplay";
import { StatusBadge } from "../components/StatusBadge";
import { formatDate } from "../utils/format";

function column(key, labelKey, render) {
  return { key, labelKey: labelKey || `field.${key}`, render };
}

function field(name, options = {}) {
  return { name, labelKey: options.labelKey || `field.${name}`, ...options };
}

function option(value, namespace = "status") {
  return { value, labelKey: `${namespace}.${value}` };
}

export const statusOptions = {
  order: [
    "new_inquiry",
    "draft_quotation",
    "waiting_availability",
    "waiting_client_confirmation",
    "confirmed",
    "scheduled",
    "in_progress",
    "installed",
    "event_running",
    "dismantling",
    "completed",
    "partially_paid",
    "fully_paid",
    "closed",
    "cancelled",
  ].map((value) => option(value, "orderStatus")),
  quotation: ["draft", "sent", "accepted", "rejected", "expired", "converted_to_order"].map((value) =>
    option(value, "quotationStatus")
  ),
  invoice: ["draft", "issued", "partially_paid", "paid", "cancelled", "overdue"].map((value) =>
    option(value, "invoiceStatus")
  ),
  payroll: ["draft", "calculated", "approved", "partially_paid", "paid"].map((value) => option(value, "payrollStatus")),
  task: ["todo", "in_progress", "done", "blocked"].map((value) => option(value)),
  trip: ["scheduled", "in_progress", "completed", "cancelled"].map((value) => option(value)),
  transaction: ["in", "out", "reserve", "release", "damage", "maintenance", "adjustment"].map((value) =>
    option(value, "option")
  ),
};

export const clientConfig = {
  endpoint: "/clients/",
  columns: [
    column("name"),
    column("client_type"),
    column("phone"),
    column("email"),
    column("balance", "field.balance", (row) => <AmountDisplay value={row.balance} />),
  ],
  fields: [
    field("name"),
    field("client_type", {
      type: "select",
      options: ["company", "person", "agency"].map((value) => option(value, "option")),
    }),
    field("phone"),
    field("email"),
    field("tax_number"),
    field("address"),
    field("credit_limit", { type: "number" }),
    field("notes"),
  ],
  defaults: { client_type: "company", credit_limit: 0 },
};

export const orderConfig = {
  endpoint: "/orders/",
  columns: [
    column("code"),
    column("title"),
    column("client_name"),
    column("start_at", "field.start_at", (row) => formatDate(row.start_at)),
    column("status", "field.status", (row) => <StatusBadge value={row.status} namespace="orderStatus" />),
    column("total_amount", "field.total_amount", (row) => <AmountDisplay value={row.total_amount} />),
  ],
  fields: [
    field("client", { type: "lookup", lookup: "/lookups/clients/", placeholderKey: "placeholder.selectClient" }),
    field("title"),
    field("event_location"),
    field("start_at", { type: "datetime" }),
    field("end_at", { type: "datetime" }),
    field("status", { type: "select", options: statusOptions.order }),
    field("revenue_amount", { type: "number" }),
    field("discount_amount", { type: "number" }),
    field("tax_amount", { type: "number" }),
    field("total_amount", { type: "number" }),
    field("notes"),
  ],
  defaults: { status: "new_inquiry", revenue_amount: 0, discount_amount: 0, tax_amount: 0, total_amount: 0 },
};

export const quotationConfig = {
  endpoint: "/quotations/",
  columns: [
    column("code"),
    column("title"),
    column("client_name"),
    column("status", "field.status", (row) => <StatusBadge value={row.status} namespace="quotationStatus" />),
    column("valid_until", "field.valid_until", (row) => formatDate(row.valid_until)),
    column("total_amount", "field.total_amount", (row) => <AmountDisplay value={row.total_amount} />),
  ],
  fields: [
    field("client", { type: "lookup", lookup: "/lookups/clients/", placeholderKey: "placeholder.selectClient" }),
    field("title"),
    field("status", { type: "select", options: statusOptions.quotation }),
    field("valid_until", { type: "date", nullable: true }),
    field("event_start_at", { type: "datetime", nullable: true }),
    field("event_end_at", { type: "datetime", nullable: true }),
    field("subtotal", { type: "number" }),
    field("discount_amount", { type: "number" }),
    field("tax_amount", { type: "number" }),
    field("total_amount", { type: "number" }),
    field("notes"),
  ],
  defaults: { status: "draft", subtotal: 0, discount_amount: 0, tax_amount: 0, total_amount: 0 },
};

export const itemConfig = {
  endpoint: "/items/",
  columns: [
    column("sku"),
    column("name"),
    column("category_name"),
    column("available_quantity"),
    column("reserved_quantity"),
    column("rental_price", "field.rental_price", (row) => <AmountDisplay value={row.rental_price} />),
  ],
  fields: [
    field("sku"),
    field("name"),
    field("category", {
      type: "lookup",
      lookup: "/lookups/item-categories/",
      placeholderKey: "placeholder.selectCategory",
    }),
    field("unit"),
    field("total_quantity", { type: "number" }),
    field("available_quantity", { type: "number" }),
    field("reserved_quantity", { type: "number" }),
    field("damaged_quantity", { type: "number" }),
    field("maintenance_quantity", { type: "number" }),
    field("rental_price", { type: "number" }),
    field("replacement_cost", { type: "number" }),
    field("location"),
  ],
  defaults: {
    unit: "pcs",
    total_quantity: 0,
    available_quantity: 0,
    reserved_quantity: 0,
    damaged_quantity: 0,
    maintenance_quantity: 0,
    rental_price: 0,
    replacement_cost: 0,
  },
};

export const vendorConfig = {
  endpoint: "/vendors/",
  columns: [
    column("name"),
    column("service_type"),
    column("phone"),
    column("balance", "field.balance", (row) => <AmountDisplay value={row.balance} />),
  ],
  fields: [
    field("name"),
    field("service_type"),
    field("phone"),
    field("email"),
    field("tax_number"),
    field("address"),
    field("payment_terms"),
  ],
};

export const driverConfig = {
  endpoint: "/drivers/",
  columns: [
    column("name"),
    column("phone"),
    column("vehicle_type"),
    column("vehicle_plate"),
    column("balance", "field.balance", (row) => <AmountDisplay value={row.balance} />),
  ],
  fields: [
    field("name"),
    field("user", { type: "lookup", lookup: "/lookups/users/", placeholderKey: "placeholder.selectUser", nullable: true }),
    field("phone"),
    field("vehicle_type"),
    field("vehicle_plate"),
    field("license_number"),
    field("day_rate", { type: "number" }),
  ],
  defaults: { day_rate: 0 },
};

export const staffConfig = {
  endpoint: "/staff/",
  columns: [
    column("name"),
    column("staff_role"),
    column("phone"),
    column("base_salary", "field.base_salary", (row) => <AmountDisplay value={row.base_salary} />),
    column("day_rate", "field.day_rate", (row) => <AmountDisplay value={row.day_rate} />),
  ],
  fields: [
    field("name"),
    field("user", { type: "lookup", lookup: "/lookups/users/", placeholderKey: "placeholder.selectUser", nullable: true }),
    field("phone"),
    field("staff_role"),
    field("hire_date", { type: "date", nullable: true }),
    field("base_salary", { type: "number" }),
    field("day_rate", { type: "number" }),
  ],
  defaults: { base_salary: 0, day_rate: 0 },
};
