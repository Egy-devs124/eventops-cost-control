from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.api import EventOpsModelViewSet
from apps.common.constants import MANAGEMENT_ROLES, ROLE_SALES
from apps.common.exception_handler import localized_message
from apps.orders.serializers import OrderSerializer
from apps.quotations.models import Quotation, QuotationItem
from apps.quotations.serializers import QuotationItemSerializer, QuotationSerializer
from apps.quotations.services import convert_quotation_to_order


QUOTATION_ROLES = MANAGEMENT_ROLES + [ROLE_SALES]


class QuotationViewSet(EventOpsModelViewSet):
    queryset = Quotation.objects.select_related("client", "created_by").prefetch_related("items").all()
    serializer_class = QuotationSerializer
    search_fields = ["code", "title", "client__name", "notes"]
    filterset_fields = ["client", "status", "valid_until"]
    ordering_fields = ["created_at", "valid_until", "total_amount"]
    allowed_roles = QUOTATION_ROLES

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="convert-to-order")
    def convert_to_order(self, request, pk=None):
        quotation = self.get_object()
        if not quotation.event_start_at or not quotation.event_end_at:
            return Response(
                {
                    "detail": localized_message(
                        request,
                        "Quotation event_start_at and event_end_at are required.",
                        "يجب إدخال تاريخ بداية ونهاية الفعالية لعرض السعر.",
                    )
                },
                status=400,
            )
        order = convert_quotation_to_order(quotation, user=request.user)
        return Response(OrderSerializer(order, context={"request": request}).data)


class QuotationItemViewSet(EventOpsModelViewSet):
    queryset = QuotationItem.objects.select_related("quotation", "item").all()
    serializer_class = QuotationItemSerializer
    search_fields = ["quotation__code", "description", "item__name"]
    filterset_fields = ["quotation", "item"]
    allowed_roles = QUOTATION_ROLES
