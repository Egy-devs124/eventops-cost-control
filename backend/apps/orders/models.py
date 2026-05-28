from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.common.constants import ORDER_STATUSES, PAYMENT_STATUSES
from apps.common.models import TimeStampedModel


class Order(TimeStampedModel):
    code = models.CharField(max_length=40, unique=True, blank=True)
    client = models.ForeignKey("clients.Client", related_name="orders", on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    event_location = models.CharField(max_length=255, blank=True)
    start_at = models.DateTimeField(db_index=True)
    end_at = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=40, choices=ORDER_STATUSES, default="new_inquiry", db_index=True)
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUSES, default="unpaid")
    revenue_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    requires_manager_approval = models.BooleanField(default=False)
    manager_override = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["status"]),
            models.Index(fields=["start_at", "end_at"]),
        ]
        ordering = ["-start_at"]

    def __str__(self):
        return f"{self.code} - {self.title}"

    def clean(self):
        if self.end_at <= self.start_at:
            raise ValidationError({"end_at": "End date must be after start date."})

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"ORD-{timezone.now():%Y%m%d%H%M%S%f}"
        self.full_clean()
        super().save(*args, **kwargs)


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey("inventory.Item", related_name="order_items", on_delete=models.PROTECT)
    description = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["order", "item"])]


class OrderStatusHistory(TimeStampedModel):
    order = models.ForeignKey(Order, related_name="status_history", on_delete=models.CASCADE)
    from_status = models.CharField(max_length=40, blank=True)
    to_status = models.CharField(max_length=40)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]


class JobSchedule(TimeStampedModel):
    order = models.OneToOneField(Order, related_name="schedule", on_delete=models.CASCADE)
    setup_start_at = models.DateTimeField()
    setup_end_at = models.DateTimeField()
    dismantle_start_at = models.DateTimeField(null=True, blank=True)
    dismantle_end_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, default="scheduled")
    notes = models.TextField(blank=True)


class JobTask(TimeStampedModel):
    order = models.ForeignKey(Order, related_name="job_tasks", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    assigned_to = models.ForeignKey(
        "staff.StaffProfile", null=True, blank=True, related_name="job_tasks", on_delete=models.SET_NULL
    )
    status = models.CharField(
        max_length=30,
        choices=[("todo", "To Do"), ("in_progress", "In Progress"), ("done", "Done"), ("blocked", "Blocked")],
        default="todo",
    )
    due_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)


class JobStaffAssignment(TimeStampedModel):
    order = models.ForeignKey(Order, related_name="staff_assignments", on_delete=models.CASCADE)
    staff = models.ForeignKey("staff.StaffProfile", related_name="job_assignments", on_delete=models.PROTECT)
    role = models.CharField(max_length=120, blank=True)
    scheduled_start_at = models.DateTimeField()
    scheduled_end_at = models.DateTimeField()
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, default="assigned")


class JobVendorAssignment(TimeStampedModel):
    order = models.ForeignKey(Order, related_name="vendor_assignments", on_delete=models.CASCADE)
    vendor = models.ForeignKey("vendors.Vendor", related_name="job_assignments", on_delete=models.PROTECT)
    service_description = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, default="assigned")


class JobDriverAssignment(TimeStampedModel):
    order = models.ForeignKey(Order, related_name="driver_assignments", on_delete=models.CASCADE)
    driver = models.ForeignKey("drivers.Driver", related_name="job_assignments", on_delete=models.PROTECT)
    pickup_location = models.CharField(max_length=255, blank=True)
    dropoff_location = models.CharField(max_length=255, blank=True)
    scheduled_at = models.DateTimeField()
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, default="assigned")
