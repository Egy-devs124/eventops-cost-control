from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.drivers.views import DriverPaymentViewSet, DriverTripViewSet, DriverViewSet


router = DefaultRouter()
router.register("trips", DriverTripViewSet)
router.register("payments", DriverPaymentViewSet)
router.register("", DriverViewSet)

urlpatterns = [path("", include(router.urls))]
