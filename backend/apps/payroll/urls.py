from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.payroll.views import PayrollLineViewSet, PayrollPeriodViewSet


router = DefaultRouter()
router.register("lines", PayrollLineViewSet)
router.register("", PayrollPeriodViewSet)

urlpatterns = [path("", include(router.urls))]
