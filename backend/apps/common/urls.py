from django.urls import path
from django.contrib.auth import get_user_model

from apps.clients.models import Client
from apps.common.lookups import lookup_view
from apps.drivers.models import Driver
from apps.finance.models import Cashbox, ExpenseCategory, Invoice, PaymentMethod
from apps.inventory.models import Item, ItemCategory
from apps.orders.models import Order
from apps.staff.models import StaffProfile
from apps.vendors.models import Vendor


urlpatterns = [
    path(
        "users/",
        lookup_view(
            get_user_model(),
            label_func=lambda obj: obj.get_full_name() or obj.email or obj.username,
            search_fields=("username", "email", "first_name", "last_name"),
        ),
        name="lookup-users",
    ),
    path("clients/", lookup_view(Client, search_fields=("name", "phone", "email")), name="lookup-clients"),
    path(
        "items/",
        lookup_view(
            Item,
            label_func=lambda obj: f"{obj.name} - {obj.sku}",
            search_fields=("name", "sku", "category__name"),
        ),
        name="lookup-items",
    ),
    path("item-categories/", lookup_view(ItemCategory), name="lookup-item-categories"),
    path("vendors/", lookup_view(Vendor, search_fields=("name", "service_type", "phone")), name="lookup-vendors"),
    path("drivers/", lookup_view(Driver, search_fields=("name", "phone", "vehicle_plate")), name="lookup-drivers"),
    path("staff/", lookup_view(StaffProfile, search_fields=("name", "staff_role", "phone")), name="lookup-staff"),
    path(
        "orders/",
        lookup_view(
            Order,
            label_func=lambda obj: f"{obj.code} - {obj.client.name}",
            search_fields=("code", "title", "client__name"),
            queryset_func=lambda: Order.objects.select_related("client").all(),
        ),
        name="lookup-orders",
    ),
    path(
        "invoices/",
        lookup_view(
            Invoice,
            label_func=lambda obj: f"{obj.code} - {obj.client.name}",
            search_fields=("code", "client__name"),
            queryset_func=lambda: Invoice.objects.select_related("client").all(),
        ),
        name="lookup-invoices",
    ),
    path("payment-methods/", lookup_view(PaymentMethod), name="lookup-payment-methods"),
    path("expense-categories/", lookup_view(ExpenseCategory), name="lookup-expense-categories"),
    path("cashboxes/", lookup_view(Cashbox), name="lookup-cashboxes"),
]
