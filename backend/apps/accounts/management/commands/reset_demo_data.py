from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from apps.accounts.models import UserProfile


BUSINESS_MODELS = [
    "attachments.Attachment",
    "notifications.Notification",
    "audit.AuditLog",
    "payroll.PayrollLine",
    "payroll.PayrollPeriod",
    "finance.Payment",
    "finance.InvoiceItem",
    "finance.Invoice",
    "finance.CashTransaction",
    "finance.Expense",
    "finance.FinancialApproval",
    "vendors.VendorPayment",
    "vendors.VendorTransaction",
    "drivers.DriverPayment",
    "drivers.DriverTrip",
    "orders.JobDriverAssignment",
    "orders.JobVendorAssignment",
    "orders.JobStaffAssignment",
    "orders.JobTask",
    "orders.JobSchedule",
    "orders.OrderStatusHistory",
    "inventory.ItemReturn",
    "inventory.ItemReservation",
    "inventory.InventoryTransaction",
    "inventory.DamageReport",
    "inventory.MaintenanceRecord",
    "orders.OrderItem",
    "quotations.QuotationItem",
    "finance.InvoiceItem",
    "quotations.Quotation",
    "orders.Order",
    "staff.StaffTask",
    "staff.StaffAdvance",
    "staff.StaffBonus",
    "staff.StaffDeduction",
    "staff.StaffProfile",
    "drivers.Driver",
    "vendors.Vendor",
    "finance.Cashbox",
    "finance.BankAccount",
    "finance.PaymentMethod",
    "finance.ExpenseCategory",
    "inventory.Item",
    "inventory.ItemCategory",
    "clients.ClientBalanceSnapshot",
    "clients.ClientContact",
    "clients.Client",
]


class Command(BaseCommand):
    help = "Clear EventOps demo/business data while preserving schema, roles, and superusers."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete-demo-users",
            action="store_true",
            help="Delete non-superuser demo users as well.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        deleted_summary = []
        for model_label in BUSINESS_MODELS:
            model = apps.get_model(model_label)
            count, _ = model.objects.all().delete()
            deleted_summary.append((model_label, count))

        if options["delete_demo_users"]:
            User = get_user_model()
            demo_users = User.objects.filter(is_superuser=False)
            UserProfile.objects.filter(user__in=demo_users).delete()
            count, _ = demo_users.delete()
            deleted_summary.append(("accounts.User(non-superuser)", count))

        self.reset_sequences()

        self.stdout.write(self.style.SUCCESS("Demo/business data reset complete."))
        for model_label, count in deleted_summary:
            if count:
                self.stdout.write(f"  deleted {count}: {model_label}")
        self.stdout.write("Roles and superusers were preserved.")

    def reset_sequences(self):
        vendor = connection.vendor
        table_names = []
        for model_label in BUSINESS_MODELS:
            model = apps.get_model(model_label)
            table_names.append(model._meta.db_table)
        with connection.cursor() as cursor:
            if vendor == "sqlite":
                existing = {
                    row[0]
                    for row in cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall()
                }
                if "sqlite_sequence" in existing:
                    for table in table_names:
                        cursor.execute("DELETE FROM sqlite_sequence WHERE name = %s", [table])
            elif vendor == "postgresql":
                for table in table_names:
                    cursor.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
