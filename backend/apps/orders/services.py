from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from apps.inventory.services import reserve_item
from apps.orders.models import OrderStatusHistory


def order_costs(order):
    item_costs = order.items.aggregate(total=Sum("cost_price"))["total"] or Decimal("0")
    staff_costs = order.staff_assignments.aggregate(total=Sum("cost"))["total"] or Decimal("0")
    vendor_costs = order.vendor_assignments.aggregate(total=Sum("cost"))["total"] or Decimal("0")
    driver_costs = order.driver_assignments.aggregate(total=Sum("cost"))["total"] or Decimal("0")
    expenses = order.expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    return {
        "item_costs": item_costs,
        "staff_costs": staff_costs,
        "vendor_costs": vendor_costs,
        "driver_costs": driver_costs,
        "expenses": expenses,
        "total_costs": item_costs + staff_costs + vendor_costs + driver_costs + expenses,
    }


def calculate_order_profit(order):
    costs = order_costs(order)
    revenue = order.total_amount or order.revenue_amount or Decimal("0")
    profit = revenue - costs["total_costs"]
    margin = Decimal("0")
    if revenue:
        margin = (profit / revenue) * Decimal("100")
    return {
        "order": order.id,
        "code": order.code,
        "order_number": order.code,
        "client": order.client.name,
        "job_title": order.title,
        "revenue": revenue,
        **costs,
        "profit": profit,
        "margin_percent": margin.quantize(Decimal("0.01")),
        "warning": profit < 0 or margin < Decimal("10"),
    }


@transaction.atomic
def set_order_status(order, status, user=None, notes=""):
    old_status = order.status
    order.status = status
    order.save(update_fields=["status", "updated_at"])
    OrderStatusHistory.objects.create(
        order=order, from_status=old_status, to_status=status, changed_by=user, notes=notes
    )
    return order


@transaction.atomic
def confirm_order(order, user=None, manager_override=False):
    for order_item in order.items.select_related("item"):
        reserve_item(
            item=order_item.item,
            order=order,
            quantity=order_item.quantity,
            start_at=order_item.start_at or order.start_at,
            end_at=order_item.end_at or order.end_at,
            user=user,
            manager_override=manager_override or order.manager_override,
        )
    return set_order_status(order, "confirmed", user=user, notes="Stock reserved on confirmation.")


def close_order(order, user=None):
    return set_order_status(order, "closed", user=user, notes="Order closed.")
