from django.conf import settings
from django.db import models

from apps.common.constants import PAYROLL_STATUSES
from apps.common.models import TimeStampedModel


class PayrollPeriod(TimeStampedModel):
    name = models.CharField(max_length=120)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    status = models.CharField(max_length=30, choices=PAYROLL_STATUSES, default="draft", db_index=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="approved_payroll_periods", on_delete=models.SET_NULL)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("start_date", "end_date")
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


class PayrollLine(TimeStampedModel):
    period = models.ForeignKey(PayrollPeriod, related_name="lines", on_delete=models.CASCADE)
    staff = models.ForeignKey("staff.StaffProfile", related_name="payroll_lines", on_delete=models.PROTECT)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    task_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    advances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=PAYROLL_STATUSES, default="draft")

    class Meta:
        unique_together = ("period", "staff")
