from rest_framework import viewsets

from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer
from apps.common.constants import MANAGEMENT_ROLES
from apps.common.permissions import RoleScopedPermission


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("user").all()
    serializer_class = AuditLogSerializer
    permission_classes = [RoleScopedPermission]
    allowed_roles = MANAGEMENT_ROLES
    search_fields = ["model_name", "object_id", "user__username"]
    filterset_fields = ["action", "model_name", "user"]
    ordering_fields = ["timestamp", "model_name"]
