from decimal import Decimal

from django.db import transaction
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from apps.payroll.models import PayrollLine
from apps.staff.models import StaffProfile


@transaction.atomic
def calculate_payroll(period):
    PayrollLine.objects.filter(period=period).delete()
    for staff in StaffProfile.objects.filter(is_active=True):
        advances = staff.advances.filter(advance_date__range=(period.start_date, period.end_date)).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        bonuses = staff.bonuses.filter(bonus_date__range=(period.start_date, period.end_date)).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        deductions = staff.deductions.filter(deduction_date__range=(period.start_date, period.end_date)).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        task_pay = staff.job_assignments.filter(
            scheduled_start_at__date__gte=period.start_date,
            scheduled_end_at__date__lte=period.end_date,
        ).aggregate(total=Sum("cost"))["total"] or Decimal("0")
        net = (staff.base_salary or Decimal("0")) + task_pay + bonuses - advances - deductions
        PayrollLine.objects.create(
            period=period,
            staff=staff,
            base_salary=staff.base_salary,
            task_pay=task_pay,
            advances=advances,
            bonuses=bonuses,
            deductions=deductions,
            net_pay=net,
            status="calculated",
        )
    period.status = "calculated"
    period.save(update_fields=["status", "updated_at"])
    return period


def approve_payroll(period, user):
    period.status = "approved"
    period.approved_by = user
    period.save(update_fields=["status", "approved_by", "updated_at"])
    period.lines.update(status="approved")
    return period


def mark_payroll_paid(period):
    period.status = "paid"
    period.paid_at = timezone.now()
    period.save(update_fields=["status", "paid_at", "updated_at"])
    period.lines.update(status="paid", paid_amount=models.F("net_pay"))
    return period
