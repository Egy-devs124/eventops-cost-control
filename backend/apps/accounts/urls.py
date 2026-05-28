from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import MeView, PermissionsView, RoleViewSet, UserViewSet


router = DefaultRouter()
router.register("roles", RoleViewSet)
router.register("users", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("me/", MeView.as_view(), name="me"),
    path("permissions/", PermissionsView.as_view(), name="permissions"),
]
