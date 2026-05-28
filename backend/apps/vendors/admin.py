from django.contrib import admin

from apps.vendors.models import Vendor, VendorPayment, VendorTransaction


admin.site.register(Vendor)
admin.site.register(VendorTransaction)
admin.site.register(VendorPayment)
