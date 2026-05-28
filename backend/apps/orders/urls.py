from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.orders.views import (
    JobDriverAssignmentViewSet,
    JobScheduleViewSet,
    JobStaffAssignmentViewSet,
    JobTaskViewSet,
    JobVendorAssignmentViewSet,
    OrderItemViewSet,
    OrderStatusHistoryViewSet,
    OrderViewSet,
)


router = DefaultRouter()
router.register("items", OrderItemViewSet)
router.register("status-history", OrderStatusHistoryViewSet)
router.register("schedules", JobScheduleViewSet)
router.register("tasks", JobTaskViewSet)
router.register("staff-assignments", JobStaffAssignmentViewSet)
router.register("vendor-assignments", JobVendorAssignmentViewSet)
router.register("driver-assignments", JobDriverAssignmentViewSet)
router.register("", OrderViewSet)

urlpatterns = [path("", include(router.urls))]
