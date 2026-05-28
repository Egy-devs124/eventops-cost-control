from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.api import EventOpsModelViewSet
from apps.common.constants import (
    FINANCE_ROLES,
    MANAGEMENT_ROLES,
    OPERATIONS_ROLES,
    ROLE_DRIVER,
    ROLE_SALES,
    ROLE_TECHNICIAN,
)
from apps.common.exception_handler import localized_message, wants_arabic
from apps.common.permissions import user_role_code
from apps.orders.models import (
    JobDriverAssignment,
    JobSchedule,
    JobStaffAssignment,
    JobTask,
    JobVendorAssignment,
    Order,
    OrderItem,
    OrderStatusHistory,
)
from apps.orders.serializers import (
    JobDriverAssignmentSerializer,
    JobScheduleSerializer,
    JobStaffAssignmentSerializer,
    JobTaskSerializer,
    JobVendorAssignmentSerializer,
    OrderItemSerializer,
    OrderSerializer,
    OrderStatusHistorySerializer,
)
from apps.orders.services import calculate_order_profit, close_order, confirm_order


ORDER_ROLES = list(set(MANAGEMENT_ROLES + OPERATIONS_ROLES + FINANCE_ROLES + [ROLE_SALES]))


class OrderViewSet(EventOpsModelViewSet):
    queryset = (
        Order.objects.select_related("client", "created_by")
        .prefetch_related("items", "status_history", "staff_assignments", "driver_assignments")
        .all()
    )
    serializer_class = OrderSerializer
    search_fields = ["code", "title", "client__name", "event_location"]
    filterset_fields = ["client", "status", "payment_status", "start_at"]
    ordering_fields = ["start_at", "created_at", "total_amount"]
    allowed_roles = ORDER_ROLES + [ROLE_TECHNICIAN, ROLE_DRIVER]

    def get_queryset(self):
        qs = super().get_queryset()
        role = user_role_code(self.request.user)
        if role == ROLE_TECHNICIAN:
            return qs.filter(staff_assignments__staff__user=self.request.user).distinct()
        if role == ROLE_DRIVER:
            return qs.filter(driver_assignments__driver__user=self.request.user).distinct()
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk=None):
        order = self.get_object()
        try:
            confirm_order(
                order,
                user=request.user,
                manager_override=bool(request.data.get("manager_override", False)),
            )
        except ValueError as exc:
            message = str(exc)
            if wants_arabic(request) and " has only " in message and " available in this date range." in message:
                item_name, rest = message.split(" has only ", 1)
                available = rest.split(" available", 1)[0]
                message = f"الصنف {item_name} لديه {available} فقط متاح في هذه الفترة."
            return Response({"detail": message}, status=400)
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        order = close_order(self.get_object(), user=request.user)
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["get"], url_path="profitability")
    def profitability(self, request, pk=None):
        role = getattr(request.user, "role", None)
        if not getattr(role, "can_view_profit", False) and not request.user.is_superuser:
            return Response(
                {
                    "detail": localized_message(
                        request,
                        "You do not have permission to view profitability.",
                        "ليس لديك صلاحية لعرض الربحية.",
                    )
                },
                status=403,
            )
        return Response(calculate_order_profit(self.get_object()))


class OrderItemViewSet(EventOpsModelViewSet):
    queryset = OrderItem.objects.select_related("order", "item").all()
    serializer_class = OrderItemSerializer
    search_fields = ["order__code", "item__name", "description"]
    filterset_fields = ["order", "item"]
    allowed_roles = ORDER_ROLES


class OrderStatusHistoryViewSet(EventOpsModelViewSet):
    queryset = OrderStatusHistory.objects.select_related("order", "changed_by").all()
    serializer_class = OrderStatusHistorySerializer
    search_fields = ["order__code", "notes"]
    filterset_fields = ["order", "to_status"]
    allowed_roles = ORDER_ROLES

    def perform_create(self, serializer):
        serializer.save(changed_by=self.request.user)


class JobScheduleViewSet(EventOpsModelViewSet):
    queryset = JobSchedule.objects.select_related("order").all()
    serializer_class = JobScheduleSerializer
    filterset_fields = ["order", "status", "setup_start_at"]
    allowed_roles = OPERATIONS_ROLES


class JobTaskViewSet(EventOpsModelViewSet):
    queryset = JobTask.objects.select_related("order", "assigned_to").all()
    serializer_class = JobTaskSerializer
    search_fields = ["order__code", "title", "notes"]
    filterset_fields = ["order", "assigned_to", "status"]
    allowed_roles = OPERATIONS_ROLES + [ROLE_TECHNICIAN]

    def get_queryset(self):
        qs = super().get_queryset()
        if user_role_code(self.request.user) == ROLE_TECHNICIAN:
            return qs.filter(assigned_to__user=self.request.user)
        return qs


class JobStaffAssignmentViewSet(EventOpsModelViewSet):
    queryset = JobStaffAssignment.objects.select_related("order", "staff").all()
    serializer_class = JobStaffAssignmentSerializer
    filterset_fields = ["order", "staff", "status"]
    search_fields = ["order__code", "staff__name", "role"]
    allowed_roles = OPERATIONS_ROLES


class JobVendorAssignmentViewSet(EventOpsModelViewSet):
    queryset = JobVendorAssignment.objects.select_related("order", "vendor").all()
    serializer_class = JobVendorAssignmentSerializer
    filterset_fields = ["order", "vendor", "status"]
    search_fields = ["order__code", "vendor__name", "service_description"]
    allowed_roles = OPERATIONS_ROLES + FINANCE_ROLES


class JobDriverAssignmentViewSet(EventOpsModelViewSet):
    queryset = JobDriverAssignment.objects.select_related("order", "driver").all()
    serializer_class = JobDriverAssignmentSerializer
    filterset_fields = ["order", "driver", "status"]
    search_fields = ["order__code", "driver__name"]
    allowed_roles = OPERATIONS_ROLES + [ROLE_DRIVER]

    def get_queryset(self):
        qs = super().get_queryset()
        if user_role_code(self.request.user) == ROLE_DRIVER:
            return qs.filter(driver__user=self.request.user)
        return qs
