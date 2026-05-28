from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.inventory.views import (
    DamageReportViewSet,
    InventoryTransactionViewSet,
    ItemCategoryViewSet,
    ItemReservationViewSet,
    ItemReturnViewSet,
    ItemViewSet,
    MaintenanceRecordViewSet,
)


router = DefaultRouter()
router.register("categories", ItemCategoryViewSet)
router.register("transactions", InventoryTransactionViewSet)
router.register("reservations", ItemReservationViewSet)
router.register("returns", ItemReturnViewSet)
router.register("maintenance", MaintenanceRecordViewSet)
router.register("damage-reports", DamageReportViewSet)
router.register("", ItemViewSet)

urlpatterns = [path("", include(router.urls))]
