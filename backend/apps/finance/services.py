from decimal import Decimal

from django.db.models import Sum


def cashbox_balance(cashbox):
    tx = cashbox.transactions.values("transaction_type").annotate(total=Sum("amount"))
    totals = {row["transaction_type"]: row["total"] for row in tx}
    return (cashbox.opening_balance or Decimal("0")) + (totals.get("in") or Decimal("0")) - (totals.get("out") or Decimal("0"))


def invoice_paid_amount(invoice):
    return invoice.payments.aggregate(total=Sum("amount"))["total"] or Decimal("0")


def update_invoice_status(invoice):
    paid = invoice_paid_amount(invoice)
    if paid <= 0:
        status = "issued" if invoice.status != "draft" else invoice.status
    elif paid < invoice.total_amount:
        status = "partially_paid"
    else:
        status = "paid"
    invoice.status = status
    invoice.save(update_fields=["status", "updated_at"])
    return invoice
