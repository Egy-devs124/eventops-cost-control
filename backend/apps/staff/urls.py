from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.staff.views import (
    StaffAdvanceViewSet,
    StaffBonusViewSet,
    StaffDeductionViewSet,
    StaffProfileViewSet,
    StaffTaskViewSet,
)


router = DefaultRouter()
router.register("tasks", StaffTaskViewSet)
router.register("advances", StaffAdvanceViewSet)
router.register("bonuses", StaffBonusViewSet)
router.register("deductions", StaffDeductionViewSet)
router.register("", StaffProfileViewSet)

urlpatterns = [path("", include(router.urls))]
