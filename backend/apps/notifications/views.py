from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.api import EventOpsModelViewSet
from apps.common.constants import ALL_ROLES
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


class NotificationViewSet(EventOpsModelViewSet):
    serializer_class = NotificationSerializer
    allowed_roles = ALL_ROLES
    filterset_fields = ["is_read"]
    search_fields = ["title", "message"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read", "updated_at"])
        return Response(self.get_serializer(notification).data)
