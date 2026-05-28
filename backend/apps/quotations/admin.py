from django.contrib import admin

from apps.quotations.models import Quotation, QuotationItem


admin.site.register(Quotation)
admin.site.register(QuotationItem)
