from apps.attachments.models import Attachment
from apps.attachments.serializers import AttachmentSerializer
from apps.common.api import EventOpsModelViewSet
from apps.common.constants import ALL_ROLES


class AttachmentViewSet(EventOpsModelViewSet):
    queryset = Attachment.objects.select_related("content_type", "uploaded_by").all()
    serializer_class = AttachmentSerializer
    search_fields = ["title", "file"]
    filterset_fields = ["content_type", "object_id"]
    allowed_roles = ALL_ROLES

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
