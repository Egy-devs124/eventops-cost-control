from django.conf import settings
from django.db import models

from apps.common.models import NamedModel, TimeStampedModel


class Vendor(NamedModel):
    service_type = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    tax_number = models.CharField(max_length=80, blank=True)
    address = models.TextField(blank=True)
    payment_terms = models.CharField(max_length=120, blank=True)


class VendorTransaction(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, related_name="transactions", on_delete=models.CASCADE)
    order = models.ForeignKey("orders.Order", null=True, blank=True, related_name="vendor_transactions", on_delete=models.SET_NULL)
    transaction_type = models.CharField(max_length=30, choices=[("cost", "Cost"), ("adjustment", "Adjustment")])
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.CharField(max_length=255)
    transaction_date = models.DateField(db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)


class VendorPayment(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, related_name="payments", on_delete=models.CASCADE)
    order = models.ForeignKey("orders.Order", null=True, blank=True, related_name="vendor_payments", on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    payment_date = models.DateField(db_index=True)
    method = models.CharField(max_length=60, default="cash")
    reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
