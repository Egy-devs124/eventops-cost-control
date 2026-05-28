from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone


def decimal_or_zero(value):
    return value or Decimal("0")


def client_balance(client):
    invoices = decimal_or_zero(client.invoices.aggregate(total=Sum("total_amount"))["total"])
    payments = decimal_or_zero(client.payments.aggregate(total=Sum("amount"))["total"])
    return invoices - payments


def vendor_balance(vendor):
    costs = decimal_or_zero(vendor.transactions.aggregate(total=Sum("amount"))["total"])
    payments = decimal_or_zero(vendor.payments.aggregate(total=Sum("amount"))["total"])
    return costs - payments


def driver_balance(driver):
    trips = decimal_or_zero(driver.trips.aggregate(total=Sum("cost"))["total"])
    payments = decimal_or_zero(driver.payments.aggregate(total=Sum("amount"))["total"])
    return trips - payments


def dashboard_metrics():
    from apps.drivers.models import Driver
    from apps.finance.models import Cashbox, Expense, Invoice, Payment
    from apps.finance.services import cashbox_balance
    from apps.inventory.models import Item
    from apps.orders.models import Order
    from apps.orders.services import calculate_order_profit
    from apps.payroll.models import PayrollLine
    from apps.quotations.models import Quotation
    from apps.vendors.models import Vendor

    today = timezone.localdate()
    month_start = today.replace(day=1)
    orders = Order.objects.all()
    revenue = decimal_or_zero(Invoice.objects.aggregate(total=Sum("total_amount"))["total"])
    collected = decimal_or_zero(Payment.objects.aggregate(total=Sum("amount"))["total"])
    cashboxes = Cashbox.objects.all()
    cash_balance = sum((cashbox_balance(c) for c in cashboxes), Decimal("0"))
    low_profit = []
    for order in orders.prefetch_related("items", "staff_assignments", "vendor_assignments", "driver_assignments", "expenses")[:50]:
        profit = calculate_order_profit(order)
        if profit["warning"]:
            low_profit.append(profit)

    return {
        "total_orders_this_month": orders.filter(start_at__date__gte=month_start).count(),
        "confirmed_jobs": orders.filter(status="confirmed").count(),
        "pending_quotations": Quotation.objects.filter(status__in=["draft", "sent"]).count(),
        "todays_jobs": orders.filter(start_at__date=today).count(),
        "upcoming_jobs": orders.filter(start_at__date__gt=today).count(),
        "total_revenue": revenue,
        "total_collected": collected,
        "outstanding_client_balances": revenue - collected,
        "vendor_payables": sum((vendor_balance(v) for v in Vendor.objects.all()), Decimal("0")),
        "driver_payables": sum((driver_balance(d) for d in Driver.objects.all()), Decimal("0")),
        "payroll_due": decimal_or_zero(PayrollLine.objects.exclude(status="paid").aggregate(total=Sum("net_pay"))["total"]),
        "cashbox_balance": cash_balance,
        "net_profit": revenue - decimal_or_zero(Expense.objects.aggregate(total=Sum("amount"))["total"]),
        "low_negative_profit_jobs": low_profit[:5],
        "items_unavailable": Item.objects.filter(available_quantity__lte=0).count(),
        "overdue_payments": Invoice.objects.filter(status="overdue").count(),
        "recent_payments": list(Payment.objects.select_related("client").order_by("-payment_date")[:8].values("id", "client__name", "amount", "payment_date")),
        "recent_expenses": list(Expense.objects.select_related("category").order_by("-expense_date")[:8].values("id", "category__name", "amount", "expense_date", "description")),
        "orders_by_status": list(orders.values("status").annotate(count=Count("id")).order_by("status")),
    }


def revenue_report():
    from apps.finance.models import Invoice, Payment

    return {
        "invoiced": list(Invoice.objects.values("issue_date").annotate(total=Sum("total_amount")).order_by("issue_date")),
        "collected": list(Payment.objects.values("payment_date").annotate(total=Sum("amount")).order_by("payment_date")),
    }


def profit_report():
    from apps.orders.models import Order
    from apps.orders.services import calculate_order_profit

    return [calculate_order_profit(order) for order in Order.objects.all()[:200]]
