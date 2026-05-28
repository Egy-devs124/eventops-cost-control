from django.conf import settings
from django.db import models

from apps.common.models import NamedModel, TimeStampedModel


class Driver(NamedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name="driver_profile", on_delete=models.SET_NULL
    )
    phone = models.CharField(max_length=50, blank=True)
    vehicle_type = models.CharField(max_length=80, blank=True)
    vehicle_plate = models.CharField(max_length=80, blank=True)
    license_number = models.CharField(max_length=120, blank=True)
    day_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)


class DriverTrip(TimeStampedModel):
    driver = models.ForeignKey(Driver, related_name="trips", on_delete=models.CASCADE)
    order = models.ForeignKey("orders.Order", null=True, blank=True, related_name="driver_trips", on_delete=models.SET_NULL)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    scheduled_at = models.DateTimeField(db_index=True)
    status = models.CharField(
        max_length=30,
        choices=[("scheduled", "Scheduled"), ("in_progress", "In Progress"), ("completed", "Completed"), ("cancelled", "Cancelled")],
        default="scheduled",
    )
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)


class DriverPayment(TimeStampedModel):
    driver = models.ForeignKey(Driver, related_name="payments", on_delete=models.CASCADE)
    trip = models.ForeignKey(DriverTrip, null=True, blank=True, related_name="payments", on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(db_index=True)
    method = models.CharField(max_length=60, default="cash")
    reference = models.CharField(max_length=120, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
