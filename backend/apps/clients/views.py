from apps.clients.models import Client, ClientBalanceSnapshot, ClientContact
from apps.clients.serializers import (
    ClientBalanceSnapshotSerializer,
    ClientContactSerializer,
    ClientSerializer,
)
from apps.common.api import EventOpsModelViewSet
from apps.common.constants import MANAGEMENT_ROLES, ROLE_ACCOUNTANT, ROLE_SALES


class ClientViewSet(EventOpsModelViewSet):
    queryset = Client.objects.prefetch_related("contacts").all()
    serializer_class = ClientSerializer
    search_fields = ["name", "phone", "email", "tax_number"]
    filterset_fields = ["client_type", "is_active"]
    ordering_fields = ["name", "created_at"]
    allowed_roles = MANAGEMENT_ROLES + [ROLE_ACCOUNTANT, ROLE_SALES]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ClientContactViewSet(EventOpsModelViewSet):
    queryset = ClientContact.objects.select_related("client").all()
    serializer_class = ClientContactSerializer
    search_fields = ["name", "phone", "email", "client__name"]
    filterset_fields = ["client", "is_primary"]
    allowed_roles = MANAGEMENT_ROLES + [ROLE_ACCOUNTANT, ROLE_SALES]


class ClientBalanceSnapshotViewSet(EventOpsModelViewSet):
    queryset = ClientBalanceSnapshot.objects.select_related("client").all()
    serializer_class = ClientBalanceSnapshotSerializer
    filterset_fields = ["client", "snapshot_date"]
    search_fields = ["client__name"]
    allowed_roles = MANAGEMENT_ROLES + [ROLE_ACCOUNTANT]
