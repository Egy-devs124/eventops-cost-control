from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import Role
from apps.clients.models import Client
from apps.common.constants import ROLE_OWNER
from apps.inventory.models import Item, ItemCategory
from apps.inventory.services import availability_for_range
from apps.orders.models import Order, OrderItem
from apps.orders.services import confirm_order


class InventoryReservationTests(TestCase):
    def setUp(self):
        role = Role.objects.create(code=ROLE_OWNER, name_en="Owner", name_ar="المالك", can_view_profit=True)
        self.user = get_user_model().objects.create_user(username="owner", password="x", role=role)
        self.client = Client.objects.create(name="Client")
        self.category = ItemCategory.objects.create(name="Screens")
        self.item = Item.objects.create(
            sku="LED-1",
            name="LED Screen",
            category=self.category,
            total_quantity=5,
            available_quantity=5,
            rental_price=Decimal("100"),
        )
        self.start = timezone.now() + timedelta(days=1)
        self.end = self.start + timedelta(days=1)

    def make_order(self, quantity):
        order = Order.objects.create(
            client=self.client,
            title="Test Job",
            start_at=self.start,
            end_at=self.end,
            total_amount=Decimal("1000"),
            created_by=self.user,
        )
        OrderItem.objects.create(order=order, item=self.item, quantity=quantity)
        return order

    def test_confirm_order_reserves_stock_and_prevents_double_booking(self):
        confirm_order(self.make_order(4), user=self.user)
        self.item.refresh_from_db()
        self.assertEqual(self.item.reserved_quantity, 4)
        self.assertEqual(availability_for_range(self.item, self.start, self.end), 1)

        with self.assertRaises(ValueError):
            confirm_order(self.make_order(2), user=self.user)

    def test_manager_override_allows_overbooking(self):
        confirm_order(self.make_order(5), user=self.user)
        overbooked = self.make_order(1)
        confirm_order(overbooked, user=self.user, manager_override=True)
        self.assertEqual(overbooked.reservations.count(), 1)
