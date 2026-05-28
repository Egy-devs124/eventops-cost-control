from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.constants import INVOICE_STATUSES
from apps.common.models import NamedModel, TimeStampedModel


class PaymentMethod(NamedModel):
    method_type = models.CharField(max_length=30, default="cash")


class BankAccount(NamedModel):
    bank_name = models.CharField(max_length=120)
    account_number = models.CharField(max_length=120, blank=True)
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)


class Cashbox(NamedModel):
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="EGP")


class CashTransaction(TimeStampedModel):
    cashbox = models.ForeignKey(Cashbox, related_name="transactions", on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=[("in", "Cash In"), ("out", "Cash Out")])
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    transaction_date = models.DateField(db_index=True)
    description = models.CharField(max_length=255)
    order = models.ForeignKey("orders.Order", null=True, blank=True, related_name="cash_transactions", on_delete=models.SET_NULL)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name="approved_cash_transactions", on_delete=models.SET_NULL
    )


class ExpenseCategory(NamedModel):
    requires_approval_above = models.DecimalField(max_digits=14, decimal_places=2, default=0)


class Expense(TimeStampedModel):
    category = models.ForeignKey(ExpenseCategory, related_name="expenses", on_delete=models.PROTECT)
    order = models.ForeignKey("orders.Order", null=True, blank=True, related_name="expenses", on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    expense_date = models.DateField(db_index=True)
    description = models.CharField(max_length=255)
    vendor = models.ForeignKey("vendors.Vendor", null=True, blank=True, related_name="expenses", on_delete=models.SET_NULL)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name="approved_expenses", on_delete=models.SET_NULL
    )
    status = models.CharField(
        max_length=20,
        choices=[("draft", "Draft"), ("pending", "Pending Approval"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="draft",
    )


class Invoice(TimeStampedModel):
    code = models.CharField(max_length=40, unique=True, blank=True)
    client = models.ForeignKey("clients.Client", related_name="invoices", on_delete=models.PROTECT)
    order = models.ForeignKey("orders.Order", null=True, blank=True, related_name="invoices", on_delete=models.SET_NULL)
    issue_date = models.DateField(default=timezone.localdate, db_index=True)
    due_date = models.DateField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=30, choices=INVOICE_STATUSES, default="draft", db_index=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"INV-{timezone.now():%Y%m%d%H%M%S%f}"
        super().save(*args, **kwargs)


class InvoiceItem(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, related_name="items", on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)


class Payment(TimeStampedModel):
    client = models.ForeignKey("clients.Client", related_name="payments", on_delete=models.PROTECT)
    order = models.ForeignKey("orders.Order", null=True, blank=True, related_name="payments", on_delete=models.SET_NULL)
    invoice = models.ForeignKey(Invoice, null=True, blank=True, related_name="payments", on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    payment_date = models.DateField(db_index=True)
    method = models.ForeignKey(PaymentMethod, null=True, blank=True, on_delete=models.SET_NULL)
    cashbox = models.ForeignKey(Cashbox, null=True, blank=True, on_delete=models.SET_NULL)
    bank_account = models.ForeignKey(BankAccount, null=True, blank=True, on_delete=models.SET_NULL)
    reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)


class FinancialApproval(TimeStampedModel):
    approval_type = models.CharField(
        max_length=40,
        choices=[
            ("high_discount", "High Discount"),
            ("negative_profit", "Negative Profit"),
            ("large_expense", "Large Expense"),
            ("manual_adjustment", "Manual Adjustment"),
            ("cashbox_correction", "Cashbox Correction"),
            ("payroll", "Payroll"),
        ],
    )
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending",
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    reason = models.TextField()
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="approval_requests", on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="financial_approvals", on_delete=models.SET_NULL)
    content_type = models.CharField(max_length=120, blank=True)
    object_id = models.CharField(max_length=120, blank=True)
