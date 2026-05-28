from rest_framework import viewsets

from apps.common.permissions import RoleScopedPermission


class EventOpsModelViewSet(viewsets.ModelViewSet):
    permission_classes = [RoleScopedPermission]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        instance = serializer.save()
        self._write_audit("create", instance, serializer.validated_data)

    def perform_update(self, serializer):
        instance = serializer.save()
        self._write_audit("update", instance, serializer.validated_data)

    def perform_destroy(self, instance):
        self._write_audit("delete", instance, {})
        instance.delete()

    def _write_audit(self, action, instance, changes):
        try:
            from apps.audit.services import log_action

            log_action(self.request.user, instance, action, changes)
        except Exception:
            # Audit should never block the core business transaction in dev.
            pass
