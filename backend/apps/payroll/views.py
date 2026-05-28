from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.api import EventOpsModelViewSet
from apps.common.constants import FINANCE_ROLES
from apps.common.exception_handler import localized_message
from apps.payroll.models import PayrollLine, PayrollPeriod
from apps.payroll.serializers import PayrollLineSerializer, PayrollPeriodSerializer
from apps.payroll.services import approve_payroll, calculate_payroll, mark_payroll_paid


class PayrollPeriodViewSet(EventOpsModelViewSet):
    queryset = PayrollPeriod.objects.prefetch_related("lines").all()
    serializer_class = PayrollPeriodSerializer
    search_fields = ["name"]
    filterset_fields = ["status", "start_date", "end_date"]
    allowed_roles = FINANCE_ROLES

    @action(detail=True, methods=["post"], url_path="calculate")
    def calculate(self, request, pk=None):
        period = calculate_payroll(self.get_object())
        return Response(self.get_serializer(period).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        period = approve_payroll(self.get_object(), request.user)
        return Response(self.get_serializer(period).data)

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        period = self.get_object()
        if period.status != "approved":
            return Response(
                {"detail": localized_message(request, "Payroll must be approved before payment.", "يجب اعتماد الرواتب قبل الدفع.")},
                status=400,
            )
        period = mark_payroll_paid(period)
        return Response(self.get_serializer(period).data)


class PayrollLineViewSet(EventOpsModelViewSet):
    queryset = PayrollLine.objects.select_related("period", "staff").all()
    serializer_class = PayrollLineSerializer
    search_fields = ["period__name", "staff__name"]
    filterset_fields = ["period", "staff", "status"]
    allowed_roles = FINANCE_ROLES
