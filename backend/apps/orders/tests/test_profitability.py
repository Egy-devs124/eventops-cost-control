from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.inventory.models import Item, ItemCategory
from apps.orders.models import JobDriverAssignment, JobStaffAssignment, JobVendorAssignment, Order, OrderItem
from apps.orders.services import calculate_order_profit
from apps.staff.models import StaffProfile
from apps.vendors.models import Vendor
from apps.drivers.models import Driver


class ProfitabilityTests(TestCase):
    def test_profitability_includes_direct_job_costs(self):
        client = Client.objects.create(name="Client")
        category = ItemCategory.objects.create(name="Screens")
        item = Item.objects.create(sku="LED-2", name="LED", category=category, total_quantity=1, available_quantity=1)
        staff = StaffProfile.objects.create(name="Tech")
        vendor = Vendor.objects.create(name="AV Vendor")
        driver = Driver.objects.create(name="Driver")
        start = timezone.now()
        order = Order.objects.create(
            client=client,
            title="Job",
            start_at=start,
            end_at=start + timedelta(days=1),
            total_amount=Decimal("10000"),
        )
        OrderItem.objects.create(order=order, item=item, quantity=1, cost_price=Decimal("1000"))
        JobStaffAssignment.objects.create(order=order, staff=staff, scheduled_start_at=start, scheduled_end_at=start, cost=Decimal("1500"))
        JobVendorAssignment.objects.create(order=order, vendor=vendor, service_description="Media", cost=Decimal("2000"))
        JobDriverAssignment.objects.create(order=order, driver=driver, scheduled_at=start, cost=Decimal("500"))

        profit = calculate_order_profit(order)
        self.assertEqual(profit["total_costs"], Decimal("5000"))
        self.assertEqual(profit["profit"], Decimal("5000"))
        self.assertEqual(profit["margin_percent"], Decimal("50.00"))
