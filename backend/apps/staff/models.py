from django.conf import settings
from django.db import models

from apps.common.models import NamedModel, TimeStampedModel


class StaffProfile(NamedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name="staff_profile", on_delete=models.SET_NULL
    )
    phone = models.CharField(max_length=50, blank=True)
    staff_role = models.CharField(max_length=120, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    day_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)


class StaffTask(TimeStampedModel):
    staff = models.ForeignKey(StaffProfile, related_name="tasks", on_delete=models.CASCADE)
    order = models.ForeignKey("orders.Order", null=True, blank=True, related_name="staff_tasks", on_delete=models.SET_NULL)
    title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=30,
        choices=[("todo", "To Do"), ("in_progress", "In Progress"), ("done", "Done"), ("blocked", "Blocked")],
        default="todo",
    )
    due_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)


class StaffAdvance(TimeStampedModel):
    staff = models.ForeignKey(StaffProfile, related_name="advances", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    advance_date = models.DateField(db_index=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)


class StaffBonus(TimeStampedModel):
    staff = models.ForeignKey(StaffProfile, related_name="bonuses", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    bonus_date = models.DateField(db_index=True)
    reason = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)


class StaffDeduction(TimeStampedModel):
    staff = models.ForeignKey(StaffProfile, related_name="deductions", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    deduction_date = models.DateField(db_index=True)
    reason = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
