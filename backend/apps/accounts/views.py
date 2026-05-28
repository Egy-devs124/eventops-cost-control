from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Role
from apps.accounts.serializers import MeSerializer, RoleSerializer, UserSerializer
from apps.common.api import EventOpsModelViewSet
from apps.common.constants import ALL_ROLES, MANAGEMENT_ROLES, ROLE_OWNER


User = get_user_model()


class RoleViewSet(EventOpsModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    search_fields = ["code", "name_en", "name_ar"]
    ordering_fields = ["code", "name_en"]
    allowed_roles = MANAGEMENT_ROLES


class UserViewSet(EventOpsModelViewSet):
    queryset = User.objects.select_related("role", "profile").all()
    serializer_class = UserSerializer
    search_fields = ["username", "first_name", "last_name", "email", "phone"]
    filterset_fields = ["role", "is_active", "is_staff"]
    ordering_fields = ["username", "date_joined"]
    allowed_roles = MANAGEMENT_ROLES


class MeView(APIView):
    def get(self, request):
        return Response(MeSerializer(request.user).data)

    def patch(self, request):
        serializer = MeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PermissionsView(APIView):
    def get(self, request):
        role = getattr(request.user, "role", None)
        code = getattr(role, "code", None)
        return Response(
            {
                "role": code,
                "all_roles": ALL_ROLES,
                "can_view_profit": bool(getattr(role, "can_view_profit", False) or code == ROLE_OWNER),
                "can_view_payroll": bool(getattr(role, "can_view_payroll", False) or code == ROLE_OWNER),
                "can_approve": bool(getattr(role, "can_approve", False) or code == ROLE_OWNER),
            }
        )
