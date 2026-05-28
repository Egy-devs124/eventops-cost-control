from django.contrib import admin

from apps.payroll.models import PayrollLine, PayrollPeriod


admin.site.register(PayrollPeriod)
admin.site.register(PayrollLine)
