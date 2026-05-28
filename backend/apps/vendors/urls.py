from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.vendors.views import VendorPaymentViewSet, VendorTransactionViewSet, VendorViewSet


router = DefaultRouter()
router.register("transactions", VendorTransactionViewSet)
router.register("payments", VendorPaymentViewSet)
router.register("", VendorViewSet)

urlpatterns = [path("", include(router.urls))]
