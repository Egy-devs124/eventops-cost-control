from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.quotations.views import QuotationItemViewSet, QuotationViewSet


router = DefaultRouter()
router.register("items", QuotationItemViewSet)
router.register("", QuotationViewSet)

urlpatterns = [path("", include(router.urls))]
