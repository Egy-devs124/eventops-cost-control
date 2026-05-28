from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.clients.views import (
    ClientBalanceSnapshotViewSet,
    ClientContactViewSet,
    ClientViewSet,
)


router = DefaultRouter()
router.register("contacts", ClientContactViewSet)
router.register("balance-snapshots", ClientBalanceSnapshotViewSet)
router.register("", ClientViewSet)

urlpatterns = [path("", include(router.urls))]
