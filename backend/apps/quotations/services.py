from django.db import transaction

from apps.orders.models import Order, OrderItem


@transaction.atomic
def convert_quotation_to_order(quotation, user=None):
    order = Order.objects.create(
        client=quotation.client,
        title=quotation.title,
        start_at=quotation.event_start_at,
        end_at=quotation.event_end_at,
        status="waiting_availability",
        revenue_amount=quotation.subtotal,
        discount_amount=quotation.discount_amount,
        tax_amount=quotation.tax_amount,
        total_amount=quotation.total_amount,
        notes=quotation.notes,
        created_by=user,
    )
    for line in quotation.items.all():
        if line.item:
            OrderItem.objects.create(
                order=order,
                item=line.item,
                description=line.description,
                quantity=line.quantity,
                unit_price=line.unit_price,
                cost_price=line.cost_price,
                start_at=quotation.event_start_at,
                end_at=quotation.event_end_at,
            )
    quotation.status = "converted_to_order"
    quotation.save(update_fields=["status", "updated_at"])
    return order
