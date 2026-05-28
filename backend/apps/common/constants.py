ROLE_OWNER = "owner_manager"
ROLE_ADMIN = "admin"
ROLE_SALES = "sales"
ROLE_OPERATIONS = "operations"
ROLE_ACCOUNTANT = "accountant"
ROLE_TECHNICIAN = "technician"
ROLE_DRIVER = "driver"
ROLE_CASHIER = "cashier"
ROLE_VIEWER = "viewer"

ALL_ROLES = [
    ROLE_OWNER,
    ROLE_ADMIN,
    ROLE_SALES,
    ROLE_OPERATIONS,
    ROLE_ACCOUNTANT,
    ROLE_TECHNICIAN,
    ROLE_DRIVER,
    ROLE_CASHIER,
    ROLE_VIEWER,
]

MANAGEMENT_ROLES = [ROLE_OWNER, ROLE_ADMIN]
FINANCE_ROLES = [ROLE_OWNER, ROLE_ACCOUNTANT]
OPERATIONS_ROLES = [ROLE_OWNER, ROLE_ADMIN, ROLE_OPERATIONS]
SALES_ROLES = [ROLE_OWNER, ROLE_ADMIN, ROLE_SALES]
CASHBOX_ROLES = [ROLE_OWNER, ROLE_ACCOUNTANT, ROLE_CASHIER]

ORDER_STATUSES = [
    ("new_inquiry", "New Inquiry"),
    ("draft_quotation", "Draft Quotation"),
    ("waiting_availability", "Waiting Availability"),
    ("waiting_client_confirmation", "Waiting Client Confirmation"),
    ("confirmed", "Confirmed"),
    ("scheduled", "Scheduled"),
    ("in_progress", "In Progress"),
    ("installed", "Installed"),
    ("event_running", "Event Running"),
    ("dismantling", "Dismantling"),
    ("completed", "Completed"),
    ("partially_paid", "Partially Paid"),
    ("fully_paid", "Fully Paid"),
    ("closed", "Closed"),
    ("cancelled", "Cancelled"),
]

QUOTATION_STATUSES = [
    ("draft", "Draft"),
    ("sent", "Sent"),
    ("accepted", "Accepted"),
    ("rejected", "Rejected"),
    ("expired", "Expired"),
    ("converted_to_order", "Converted to Order"),
]

INVOICE_STATUSES = [
    ("draft", "Draft"),
    ("issued", "Issued"),
    ("partially_paid", "Partially Paid"),
    ("paid", "Paid"),
    ("cancelled", "Cancelled"),
    ("overdue", "Overdue"),
]

PAYMENT_STATUSES = [
    ("unpaid", "Unpaid"),
    ("partially_paid", "Partially Paid"),
    ("fully_paid", "Fully Paid"),
    ("overpaid", "Overpaid"),
    ("refunded", "Refunded"),
]

PAYROLL_STATUSES = [
    ("draft", "Draft"),
    ("calculated", "Calculated"),
    ("approved", "Approved"),
    ("partially_paid", "Partially Paid"),
    ("paid", "Paid"),
]
