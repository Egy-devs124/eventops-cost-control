from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.api import EventOpsModelViewSet
from apps.common.constants import MANAGEMENT_ROLES, OPERATIONS_ROLES, ROLE_ACCOUNTANT, ROLE_SALES
from apps.common.exception_handler import localized_message
from apps.inventory.models import (
    DamageReport,
    InventoryTransaction,
    Item,
    ItemCategory,
    ItemReservation,
    ItemReturn,
    MaintenanceRecord,
)
from apps.inventory.serializers import (
    DamageReportSerializer,
    InventoryTransactionSerializer,
    ItemCategorySerializer,
    ItemReservationSerializer,
    ItemReturnSerializer,
    ItemSerializer,
    MaintenanceRecordSerializer,
)
from apps.inventory.services import availability_for_range


INVENTORY_ROLES = list(set(OPERATIONS_ROLES + MANAGEMENT_ROLES + [ROLE_ACCOUNTANT, ROLE_SALES]))


class ItemCategoryViewSet(EventOpsModelViewSet):
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer
    search_fields = ["name"]
    allowed_roles = INVENTORY_ROLES


class ItemViewSet(EventOpsModelViewSet):
    queryset = Item.objects.select_related("category").all()
    serializer_class = ItemSerializer
    search_fields = ["name", "sku", "category__name", "location"]
    filterset_fields = ["category", "is_active"]
    ordering_fields = ["name", "sku", "available_quantity", "rental_price"]
    allowed_roles = INVENTORY_ROLES

    @action(detail=False, methods=["get"], url_path="availability")
    def availability(self, request):
        start_at = request.query_params.get("start_at")
        end_at = request.query_params.get("end_at")
        if not start_at or not end_at:
            return Response(
                {"detail": localized_message(request, "start_at and end_at are required.", "يجب إدخال تاريخ البداية والنهاية.")},
                status=400,
            )
        data = []
        for item in self.filter_queryset(self.get_queryset()):
            data.append(
                {
                    "id": item.id,
                    "sku": item.sku,
                    "name": item.name,
                    "available_quantity": availability_for_range(item, start_at, end_at),
                    "total_quantity": item.total_quantity,
                }
            )
        return Response(data)


class InventoryTransactionViewSet(EventOpsModelViewSet):
    queryset = InventoryTransaction.objects.select_related("item", "order").all()
    serializer_class = InventoryTransactionSerializer
    filterset_fields = ["item", "transaction_type", "order"]
    search_fields = ["item__name", "item__sku", "reference", "notes"]
    allowed_roles = INVENTORY_ROLES

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ItemReservationViewSet(EventOpsModelViewSet):
    queryset = ItemReservation.objects.select_related("item", "order").all()
    serializer_class = ItemReservationSerializer
    filterset_fields = ["item", "order", "status"]
    search_fields = ["item__name", "order__code"]
    allowed_roles = INVENTORY_ROLES


class ItemReturnViewSet(EventOpsModelViewSet):
    queryset = ItemReturn.objects.select_related("reservation", "reservation__item").all()
    serializer_class = ItemReturnSerializer
    allowed_roles = INVENTORY_ROLES

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)


class MaintenanceRecordViewSet(EventOpsModelViewSet):
    queryset = MaintenanceRecord.objects.select_related("item").all()
    serializer_class = MaintenanceRecordSerializer
    filterset_fields = ["item", "status"]
    search_fields = ["item__name", "notes"]
    allowed_roles = OPERATIONS_ROLES


class DamageReportViewSet(EventOpsModelViewSet):
    queryset = DamageReport.objects.select_related("item", "order").all()
    serializer_class = DamageReportSerializer
    filterset_fields = ["item", "order", "severity"]
    search_fields = ["item__name", "notes"]
    allowed_roles = OPERATIONS_ROLES
