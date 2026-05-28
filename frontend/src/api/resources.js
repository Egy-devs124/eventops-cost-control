import { api } from "./client";

export const resources = {
  clients: "/clients/",
  orders: "/orders/",
  quotations: "/quotations/",
  items: "/items/",
  vendors: "/vendors/",
  drivers: "/drivers/",
  staff: "/staff/",
  payroll: "/payroll/",
  payments: "/finance/payments/",
  expenses: "/finance/expenses/",
  cashboxes: "/finance/cashboxes/",
  invoices: "/finance/invoices/",
  approvals: "/finance/approvals/",
  notifications: "/notifications/",
};

export function fetchResource(endpoint, params = {}) {
  return api.get(endpoint, { params });
}

export function createResource(endpoint, payload) {
  return api.post(endpoint, payload);
}

export function updateResource(endpoint, id, payload) {
  return api.patch(`${endpoint}${id}/`, payload);
}

export function deleteResource(endpoint, id) {
  return api.delete(`${endpoint}${id}/`);
}
