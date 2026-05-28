from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import Role, UserProfile
from apps.clients.models import Client, ClientContact
from apps.common.constants import (
    ALL_ROLES,
    ROLE_ACCOUNTANT,
    ROLE_ADMIN,
    ROLE_CASHIER,
    ROLE_DRIVER,
    ROLE_OPERATIONS,
    ROLE_OWNER,
    ROLE_SALES,
    ROLE_TECHNICIAN,
    ROLE_VIEWER,
)
from apps.drivers.models import Driver, DriverPayment, DriverTrip
from apps.finance.models import (
    CashTransaction,
    Cashbox,
    Expense,
    ExpenseCategory,
    Invoice,
    InvoiceItem,
    Payment,
    PaymentMethod,
)
from apps.inventory.models import Item, ItemCategory
from apps.notifications.models import Notification
from apps.orders.models import (
    JobDriverAssignment,
    JobSchedule,
    JobStaffAssignment,
    JobTask,
    JobVendorAssignment,
    Order,
    OrderItem,
)
from apps.orders.services import confirm_order
from apps.payroll.models import PayrollPeriod
from apps.payroll.services import calculate_payroll
from apps.quotations.models import Quotation, QuotationItem
from apps.staff.models import StaffAdvance, StaffBonus, StaffDeduction, StaffProfile
from apps.vendors.models import Vendor, VendorPayment, VendorTransaction


ROLE_LABELS = {
    ROLE_OWNER: ("Owner / Manager", "المالك / المدير"),
    ROLE_ADMIN: ("Admin", "مسؤول النظام"),
    ROLE_SALES: ("Sales Staff", "المبيعات"),
    ROLE_OPERATIONS: ("Operations Manager", "مدير التشغيل"),
    ROLE_ACCOUNTANT: ("Accountant", "المحاسب"),
    ROLE_TECHNICIAN: ("Technician", "فني"),
    ROLE_DRIVER: ("Driver", "سائق"),
    ROLE_CASHIER: ("Cashier", "أمين الصندوق"),
    ROLE_VIEWER: ("Viewer", "مشاهد"),
}

DEMO_USERNAMES = {
    ROLE_OWNER: "owner",
    ROLE_ADMIN: "admin",
    ROLE_SALES: "sales",
    ROLE_OPERATIONS: "operations",
    ROLE_ACCOUNTANT: "accountant",
    ROLE_TECHNICIAN: "technician",
    ROLE_DRIVER: "driver",
    ROLE_CASHIER: "cashier",
    ROLE_VIEWER: "viewer",
}


class Command(BaseCommand):
    help = "Seed demo data for EventOps Cost Control System."

    def handle(self, *args, **options):
        User = get_user_model()
        roles = {}
        for code in ALL_ROLES:
            name_en, name_ar = ROLE_LABELS[code]
            role, _ = Role.objects.update_or_create(
                code=code,
                defaults={
                    "name_en": name_en,
                    "name_ar": name_ar,
                    "can_view_profit": code in [ROLE_OWNER, ROLE_ACCOUNTANT],
                    "can_view_payroll": code in [ROLE_OWNER, ROLE_ACCOUNTANT],
                    "can_approve": code in [ROLE_OWNER, ROLE_ADMIN],
                },
            )
            roles[code] = role

        users = {}
        for code in ALL_ROLES:
            username = DEMO_USERNAMES[code]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@eventops.local",
                    "first_name": ROLE_LABELS[code][0].split()[0],
                    "role": roles[code],
                    "is_staff": code in [ROLE_OWNER, ROLE_ADMIN],
                    "is_superuser": code == ROLE_OWNER,
                },
            )
            if created:
                user.set_password("eventops123")
                user.save()
            if user.role_id != roles[code].id:
                user.role = roles[code]
                user.save(update_fields=["role"])
            UserProfile.objects.get_or_create(user=user)
            users[code] = user

        vip, _ = Client.objects.get_or_create(
            name="Nile Conference Center",
            defaults={
                "client_type": "company",
                "phone": "+20 100 000 0101",
                "email": "events@nile.example",
                "address": "New Cairo",
                "credit_limit": Decimal("250000"),
                "created_by": users[ROLE_SALES],
            },
        )
        ClientContact.objects.get_or_create(
            client=vip,
            name="Mona Hassan",
            defaults={"phone": "+20 100 100 1001", "email": "mona@nile.example", "is_primary": True},
        )
        agency, _ = Client.objects.get_or_create(
            name="Cairo Brand Activations",
            defaults={"client_type": "agency", "phone": "+20 100 000 0202", "created_by": users[ROLE_SALES]},
        )

        screens, _ = ItemCategory.objects.get_or_create(name="Screens")
        sound, _ = ItemCategory.objects.get_or_create(name="Sound Systems")
        lighting, _ = ItemCategory.objects.get_or_create(name="Lighting")
        furniture, _ = ItemCategory.objects.get_or_create(name="Wooden Work & Tables")
        led, _ = Item.objects.get_or_create(
            sku="LED-P3-001",
            defaults={
                "name": "Indoor LED Screen P3",
                "category": screens,
                "total_quantity": 20,
                "available_quantity": 20,
                "rental_price": Decimal("1500"),
                "replacement_cost": Decimal("8000"),
            },
        )
        speaker, _ = Item.objects.get_or_create(
            sku="SND-JBL-001",
            defaults={
                "name": "JBL Speaker Set",
                "category": sound,
                "total_quantity": 12,
                "available_quantity": 12,
                "rental_price": Decimal("750"),
                "replacement_cost": Decimal("4500"),
            },
        )
        moving_head, _ = Item.objects.get_or_create(
            sku="LGT-MH-001",
            defaults={
                "name": "Moving Head Light",
                "category": lighting,
                "total_quantity": 16,
                "available_quantity": 16,
                "rental_price": Decimal("350"),
                "replacement_cost": Decimal("2500"),
            },
        )
        table, _ = Item.objects.get_or_create(
            sku="TBL-WD-001",
            defaults={
                "name": "Wooden Registration Table",
                "category": furniture,
                "total_quantity": 10,
                "available_quantity": 10,
                "rental_price": Decimal("400"),
                "replacement_cost": Decimal("1800"),
            },
        )

        av_vendor, _ = Vendor.objects.get_or_create(
            name="Delta AV Rentals",
            defaults={"service_type": "External screens and media equipment", "phone": "+20 111 222 3333"},
        )
        wood_vendor, _ = Vendor.objects.get_or_create(
            name="Craft Wood Works",
            defaults={"service_type": "Custom wooden production", "phone": "+20 111 222 4444"},
        )

        tech_staff, _ = StaffProfile.objects.get_or_create(
            name="Ahmed Technician",
            defaults={"user": users[ROLE_TECHNICIAN], "phone": "+20 122 111 1111", "staff_role": "LED Technician", "base_salary": Decimal("8000"), "day_rate": Decimal("700")},
        )
        ops_staff, _ = StaffProfile.objects.get_or_create(
            name="Sara Operations",
            defaults={"user": users[ROLE_OPERATIONS], "phone": "+20 122 222 2222", "staff_role": "Operations Lead", "base_salary": Decimal("14000"), "day_rate": Decimal("1000")},
        )
        driver, _ = Driver.objects.get_or_create(
            name="Hossam Driver",
            defaults={"user": users[ROLE_DRIVER], "phone": "+20 122 333 3333", "vehicle_type": "Truck", "vehicle_plate": "EGY-2457", "day_rate": Decimal("650")},
        )

        now = timezone.now()
        order, _ = Order.objects.get_or_create(
            code="ORD-DEMO-001",
            defaults={
                "client": vip,
                "title": "Annual Medical Conference Setup",
                "event_location": "Nile Conference Center - Hall A",
                "start_at": now + timedelta(days=5),
                "end_at": now + timedelta(days=6),
                "status": "waiting_availability",
                "revenue_amount": Decimal("95000"),
                "discount_amount": Decimal("5000"),
                "tax_amount": Decimal("0"),
                "total_amount": Decimal("90000"),
                "created_by": users[ROLE_SALES],
            },
        )
        OrderItem.objects.get_or_create(order=order, item=led, defaults={"quantity": 8, "unit_price": Decimal("1500"), "cost_price": Decimal("5000")})
        OrderItem.objects.get_or_create(order=order, item=speaker, defaults={"quantity": 4, "unit_price": Decimal("750"), "cost_price": Decimal("1200")})
        OrderItem.objects.get_or_create(order=order, item=moving_head, defaults={"quantity": 6, "unit_price": Decimal("350"), "cost_price": Decimal("900")})
        JobSchedule.objects.get_or_create(
            order=order,
            defaults={
                "setup_start_at": now + timedelta(days=4, hours=8),
                "setup_end_at": now + timedelta(days=4, hours=18),
                "dismantle_start_at": now + timedelta(days=6, hours=20),
                "dismantle_end_at": now + timedelta(days=7, hours=2),
            },
        )
        JobStaffAssignment.objects.get_or_create(
            order=order,
            staff=tech_staff,
            defaults={"role": "LED installation", "scheduled_start_at": now + timedelta(days=4), "scheduled_end_at": now + timedelta(days=6), "cost": Decimal("2500")},
        )
        JobVendorAssignment.objects.get_or_create(
            order=order,
            vendor=av_vendor,
            defaults={"service_description": "Backup media server", "cost": Decimal("6000")},
        )
        JobDriverAssignment.objects.get_or_create(
            order=order,
            driver=driver,
            defaults={"pickup_location": "Warehouse", "dropoff_location": "Nile Conference Center", "scheduled_at": now + timedelta(days=4), "cost": Decimal("1200")},
        )
        JobTask.objects.get_or_create(order=order, title="Install LED wall and run media test", defaults={"assigned_to": tech_staff, "status": "todo", "due_at": now + timedelta(days=4, hours=16)})
        if order.status == "waiting_availability" and not order.reservations.exists():
            confirm_order(order, user=users[ROLE_OPERATIONS])

        quotation, _ = Quotation.objects.get_or_create(
            code="QTN-DEMO-001",
            defaults={
                "client": agency,
                "title": "Mall Brand Activation Booth",
                "status": "sent",
                "valid_until": timezone.localdate() + timedelta(days=14),
                "event_start_at": now + timedelta(days=12),
                "event_end_at": now + timedelta(days=13),
                "subtotal": Decimal("42000"),
                "discount_amount": Decimal("2000"),
                "total_amount": Decimal("40000"),
                "created_by": users[ROLE_SALES],
            },
        )
        QuotationItem.objects.get_or_create(quotation=quotation, description="Wooden booth and registration table", defaults={"item": table, "quantity": 2, "unit_price": Decimal("8000"), "cost_price": Decimal("5000"), "line_total": Decimal("16000")})
        QuotationItem.objects.get_or_create(quotation=quotation, description="Sound and lighting package", defaults={"item": speaker, "quantity": 2, "unit_price": Decimal("4500"), "cost_price": Decimal("2500"), "line_total": Decimal("9000")})

        invoice, _ = Invoice.objects.get_or_create(
            code="INV-DEMO-001",
            defaults={"client": vip, "order": order, "status": "issued", "subtotal": Decimal("90000"), "total_amount": Decimal("90000"), "created_by": users[ROLE_ACCOUNTANT]},
        )
        InvoiceItem.objects.get_or_create(invoice=invoice, description="Event installation package", defaults={"quantity": 1, "unit_price": Decimal("90000"), "line_total": Decimal("90000")})
        cash_method, _ = PaymentMethod.objects.get_or_create(name="Cash", defaults={"method_type": "cash"})
        bank_method, _ = PaymentMethod.objects.get_or_create(name="Bank Transfer", defaults={"method_type": "bank"})
        main_cashbox, _ = Cashbox.objects.get_or_create(name="Main Cashbox", defaults={"opening_balance": Decimal("15000"), "currency": "EGP"})
        Payment.objects.get_or_create(client=vip, invoice=invoice, amount=Decimal("35000"), defaults={"order": order, "payment_date": timezone.localdate(), "method": cash_method, "cashbox": main_cashbox, "created_by": users[ROLE_ACCOUNTANT]})
        CashTransaction.objects.get_or_create(cashbox=main_cashbox, amount=Decimal("35000"), transaction_type="in", defaults={"transaction_date": timezone.localdate(), "description": "Client collection for INV-DEMO-001", "order": order, "created_by": users[ROLE_CASHIER]})
        fuel_cat, _ = ExpenseCategory.objects.get_or_create(name="Fuel", defaults={"requires_approval_above": Decimal("5000")})
        production_cat, _ = ExpenseCategory.objects.get_or_create(name="External Production", defaults={"requires_approval_above": Decimal("10000")})
        Expense.objects.get_or_create(category=fuel_cat, order=order, amount=Decimal("950"), defaults={"expense_date": timezone.localdate(), "description": "Truck fuel", "status": "approved", "created_by": users[ROLE_ACCOUNTANT]})
        Expense.objects.get_or_create(category=production_cat, order=order, vendor=wood_vendor, amount=Decimal("6500"), defaults={"expense_date": timezone.localdate(), "description": "Custom stage fascia", "status": "approved", "created_by": users[ROLE_ACCOUNTANT]})
        VendorTransaction.objects.get_or_create(vendor=av_vendor, order=order, amount=Decimal("6000"), defaults={"transaction_type": "cost", "description": "Backup media server", "transaction_date": timezone.localdate(), "created_by": users[ROLE_ACCOUNTANT]})
        VendorPayment.objects.get_or_create(vendor=av_vendor, order=order, amount=Decimal("2500"), defaults={"payment_date": timezone.localdate(), "method": "cash", "created_by": users[ROLE_ACCOUNTANT]})
        DriverTrip.objects.get_or_create(driver=driver, order=order, pickup_location="Warehouse", dropoff_location="Nile Conference Center", defaults={"scheduled_at": now + timedelta(days=4), "status": "scheduled", "cost": Decimal("1200")})
        DriverPayment.objects.get_or_create(driver=driver, amount=Decimal("500"), defaults={"payment_date": timezone.localdate(), "method": "cash", "created_by": users[ROLE_ACCOUNTANT]})
        StaffAdvance.objects.get_or_create(staff=tech_staff, amount=Decimal("1000"), defaults={"advance_date": timezone.localdate(), "created_by": users[ROLE_ACCOUNTANT]})
        StaffBonus.objects.get_or_create(staff=tech_staff, amount=Decimal("500"), defaults={"bonus_date": timezone.localdate(), "reason": "Urgent setup bonus", "created_by": users[ROLE_ACCOUNTANT]})
        StaffDeduction.objects.get_or_create(staff=tech_staff, amount=Decimal("150"), defaults={"deduction_date": timezone.localdate(), "reason": "Late attendance", "created_by": users[ROLE_ACCOUNTANT]})
        period, _ = PayrollPeriod.objects.get_or_create(
            start_date=timezone.localdate().replace(day=1),
            end_date=timezone.localdate(),
            defaults={"name": timezone.localdate().strftime("%B %Y Payroll")},
        )
        if not period.lines.exists():
            calculate_payroll(period)
        Notification.objects.get_or_create(
            user=users[ROLE_OWNER],
            title="Demo data is ready",
            defaults={"message": "EventOps demo data has been seeded. Login with owner / eventops123."},
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded. Login as owner / eventops123."))
