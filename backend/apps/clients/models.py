from django.conf import settings
from django.db import models

from apps.common.models import NamedModel, TimeStampedModel


class Client(NamedModel):
    client_type = models.CharField(
        max_length=30,
        choices=[("company", "Company"), ("person", "Person"), ("agency", "Agency")],
        default="company",
    )
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    tax_number = models.CharField(max_length=80, blank=True)
    address = models.TextField(blank=True)
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["email"]),
        ]


class ClientContact(TimeStampedModel):
    client = models.ForeignKey(Client, related_name="contacts", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.client.name}"


class ClientBalanceSnapshot(TimeStampedModel):
    client = models.ForeignKey(Client, related_name="balance_snapshots", on_delete=models.CASCADE)
    snapshot_date = models.DateField(db_index=True)
    invoiced_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        unique_together = ("client", "snapshot_date")
        ordering = ["-snapshot_date"]
