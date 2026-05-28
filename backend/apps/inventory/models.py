from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import NamedModel, TimeStampedModel


class ItemCategory(NamedModel):
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = "Item categories"


class Item(NamedModel):
    sku = models.CharField(max_length=80, unique=True)
    category = models.ForeignKey(ItemCategory, related_name="items", on_delete=models.PROTECT)
    unit = models.CharField(max_length=30, default="pcs")
    total_quantity = models.PositiveIntegerField(default=0)
    available_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    damaged_quantity = models.PositiveIntegerField(default=0)
    maintenance_quantity = models.PositiveIntegerField(default=0)
    rental_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    replacement_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    location = models.CharField(max_length=120, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["name"]),
            models.Index(fields=["category"]),
        ]

    def recalculate_available(self):
        self.available_quantity = max(
            self.total_quantity
            - self.reserved_quantity
            - self.damaged_quantity
            - self.maintenance_quantity,
            0,
        )
        return self.available_quantity


class InventoryTransaction(TimeStampedModel):
    item = models.ForeignKey(Item, related_name="transactions", on_delete=models.CASCADE)
    transaction_type = models.CharField(
        max_length=30,
        choices=[
            ("in", "In"),
            ("out", "Out"),
            ("reserve", "Reserve"),
            ("release", "Release"),
            ("damage", "Damage"),
            ("maintenance", "Maintenance"),
            ("adjustment", "Adjustment"),
        ],
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    order = models.ForeignKey(
        "orders.Order", null=True, blank=True, related_name="inventory_transactions", on_delete=models.SET_NULL
    )
    reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["-created_at"]


class ItemReservation(TimeStampedModel):
    item = models.ForeignKey(Item, related_name="reservations", on_delete=models.CASCADE)
    order = models.ForeignKey("orders.Order", related_name="reservations", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    start_at = models.DateTimeField(db_index=True)
    end_at = models.DateTimeField(db_index=True)
    status = models.CharField(
        max_length=20,
        choices=[("reserved", "Reserved"), ("out", "Out on Job"), ("returned", "Returned"), ("cancelled", "Cancelled")],
        default="reserved",
        db_index=True,
    )
    manager_override = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["item", "start_at", "end_at", "status"])]


class ItemReturn(TimeStampedModel):
    reservation = models.ForeignKey(ItemReservation, related_name="returns", on_delete=models.CASCADE)
    returned_quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    damaged_quantity = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )


class MaintenanceRecord(TimeStampedModel):
    item = models.ForeignKey(Item, related_name="maintenance_records", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("open", "Open"), ("in_progress", "In Progress"), ("done", "Done")],
        default="open",
    )
    notes = models.TextField(blank=True)


class DamageReport(TimeStampedModel):
    item = models.ForeignKey(Item, related_name="damage_reports", on_delete=models.CASCADE)
    order = models.ForeignKey("orders.Order", null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
    severity = models.CharField(max_length=20, choices=[("minor", "Minor"), ("major", "Major"), ("lost", "Lost")])
    repair_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
