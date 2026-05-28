from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.constants import QUOTATION_STATUSES
from apps.common.models import TimeStampedModel


class Quotation(TimeStampedModel):
    code = models.CharField(max_length=40, unique=True, blank=True)
    client = models.ForeignKey("clients.Client", related_name="quotations", on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=40, choices=QUOTATION_STATUSES, default="draft", db_index=True)
    valid_until = models.DateField(null=True, blank=True)
    event_start_at = models.DateTimeField(null=True, blank=True)
    event_end_at = models.DateTimeField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"QTN-{timezone.now():%Y%m%d%H%M%S%f}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.title}"


class QuotationItem(TimeStampedModel):
    quotation = models.ForeignKey(Quotation, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey("inventory.Item", null=True, blank=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
