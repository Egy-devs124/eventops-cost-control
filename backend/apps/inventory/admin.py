from django.contrib import admin

from apps.inventory.models import (
    DamageReport,
    InventoryTransaction,
    Item,
    ItemCategory,
    ItemReservation,
    ItemReturn,
    MaintenanceRecord,
)


admin.site.register(ItemCategory)
admin.site.register(Item)
admin.site.register(InventoryTransaction)
admin.site.register(ItemReservation)
admin.site.register(ItemReturn)
admin.site.register(MaintenanceRecord)
admin.site.register(DamageReport)
