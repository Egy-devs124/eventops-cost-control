from django.contrib import admin

from apps.drivers.models import Driver, DriverPayment, DriverTrip


admin.site.register(Driver)
admin.site.register(DriverTrip)
admin.site.register(DriverPayment)
