from django.contrib import admin

from apps.staff.models import StaffAdvance, StaffBonus, StaffDeduction, StaffProfile, StaffTask


admin.site.register(StaffProfile)
admin.site.register(StaffTask)
admin.site.register(StaffAdvance)
admin.site.register(StaffBonus)
admin.site.register(StaffDeduction)
