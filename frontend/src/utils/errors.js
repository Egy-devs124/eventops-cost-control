const ERROR_KEY_MAP = {
  "This field is required.": "validation.required",
  "This field may not be null.": "validation.required",
  "This field may not be blank.": "validation.required",
  "Invalid choice.": "validation.invalidChoice",
  "Invalid choice": "validation.invalidChoice",
  "Permission denied": "validation.permissionDenied",
  "You do not have permission to perform this action.": "validation.permissionDenied",
  "Authentication credentials were not provided.": "validation.notAuthenticated",
  "End date must be after start date.": "validation.endAfterStart",
  "Quotation event_start_at and event_end_at are required.": "validation.quotationDatesRequired",
  "start_at and end_at are required.": "validation.availabilityDatesRequired",
  "Payroll must be approved before payment.": "validation.payrollApproveFirst",
};

function translateString(value, t) {
  if (!value) return "";
  const normalized = String(value);
  if (ERROR_KEY_MAP[normalized]) return t(ERROR_KEY_MAP[normalized]);
  const invalidChoiceMatch = normalized.match(/^"?.+"? is not a valid choice\.$/);
  if (invalidChoiceMatch) return t("validation.invalidChoice");
  return normalized;
}

export function formatApiError(errorData, t) {
  if (!errorData) return t("message.networkError");
  if (typeof errorData === "string") return translateString(errorData, t);
  if (Array.isArray(errorData)) return errorData.map((item) => formatApiError(item, t)).join("\n");
  if (typeof errorData === "object") {
    if (errorData.detail) return translateString(errorData.detail, t);
    return Object.entries(errorData)
      .map(([field, messages]) => `${t(`field.${field}`, field)}: ${formatApiError(messages, t)}`)
      .join("\n");
  }
  return String(errorData);
}
