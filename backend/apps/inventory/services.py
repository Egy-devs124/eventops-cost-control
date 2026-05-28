from django.db import transaction
from django.db.models import Sum

from apps.inventory.models import InventoryTransaction, ItemReservation


def reserved_quantity_for_range(item, start_at, end_at, exclude_order=None):
    qs = ItemReservation.objects.filter(
        item=item,
        status__in=["reserved", "out"],
        start_at__lt=end_at,
        end_at__gt=start_at,
    )
    if exclude_order:
        qs = qs.exclude(order=exclude_order)
    return qs.aggregate(total=Sum("quantity"))["total"] or 0


def availability_for_range(item, start_at, end_at, exclude_order=None):
    reserved = reserved_quantity_for_range(item, start_at, end_at, exclude_order)
    base_available = max(item.total_quantity - item.damaged_quantity - item.maintenance_quantity, 0)
    return max(base_available - reserved, 0)


@transaction.atomic
def reserve_item(item, order, quantity, start_at, end_at, user=None, manager_override=False):
    available = availability_for_range(item, start_at, end_at, exclude_order=order)
    if quantity > available and not manager_override:
        raise ValueError(f"{item.name} has only {available} available in this date range.")

    reservation = ItemReservation.objects.create(
        item=item,
        order=order,
        quantity=quantity,
        start_at=start_at,
        end_at=end_at,
        manager_override=manager_override,
    )
    item.reserved_quantity = ItemReservation.objects.filter(
        item=item, status__in=["reserved", "out"]
    ).aggregate(total=Sum("quantity"))["total"] or 0
    item.recalculate_available()
    item.save(update_fields=["reserved_quantity", "available_quantity", "updated_at"])
    InventoryTransaction.objects.create(
        item=item,
        order=order,
        transaction_type="reserve",
        quantity=quantity,
        created_by=user,
        reference=f"Reservation #{reservation.id}",
    )
    return reservation


@transaction.atomic
def return_reservation(reservation, returned_quantity, damaged_quantity=0, user=None, notes=""):
    reservation.status = "returned"
    reservation.save(update_fields=["status", "updated_at"])
    item = reservation.item
    item.reserved_quantity = max(item.reserved_quantity - returned_quantity, 0)
    item.damaged_quantity += damaged_quantity
    item.recalculate_available()
    item.save(update_fields=["reserved_quantity", "damaged_quantity", "available_quantity", "updated_at"])
    InventoryTransaction.objects.create(
        item=item,
        order=reservation.order,
        transaction_type="release",
        quantity=returned_quantity,
        created_by=user,
        notes=notes,
    )
    if damaged_quantity:
        InventoryTransaction.objects.create(
            item=item,
            order=reservation.order,
            transaction_type="damage",
            quantity=damaged_quantity,
            created_by=user,
            notes=notes,
        )
