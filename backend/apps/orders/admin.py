from django.contrib import admin

from apps.orders.models import (
    JobDriverAssignment,
    JobSchedule,
    JobStaffAssignment,
    JobTask,
    JobVendorAssignment,
    Order,
    OrderItem,
    OrderStatusHistory,
)


admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderStatusHistory)
admin.site.register(JobSchedule)
admin.site.register(JobTask)
admin.site.register(JobStaffAssignment)
admin.site.register(JobVendorAssignment)
admin.site.register(JobDriverAssignment)
