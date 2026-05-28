from apps.common.api import EventOpsModelViewSet
from apps.common.constants import FINANCE_ROLES, MANAGEMENT_ROLES, OPERATIONS_ROLES, ROLE_TECHNICIAN
from apps.common.permissions import user_role_code
from apps.staff.models import StaffAdvance, StaffBonus, StaffDeduction, StaffProfile, StaffTask
from apps.staff.serializers import (
    StaffAdvanceSerializer,
    StaffBonusSerializer,
    StaffDeductionSerializer,
    StaffProfileSerializer,
    StaffTaskSerializer,
)


STAFF_ROLES = list(set(MANAGEMENT_ROLES + OPERATIONS_ROLES + FINANCE_ROLES))


class StaffProfileViewSet(EventOpsModelViewSet):
    queryset = StaffProfile.objects.select_related("user").all()
    serializer_class = StaffProfileSerializer
    search_fields = ["name", "phone", "staff_role"]
    filterset_fields = ["is_active", "staff_role"]
    allowed_roles = STAFF_ROLES


class StaffTaskViewSet(EventOpsModelViewSet):
    queryset = StaffTask.objects.select_related("staff", "staff__user", "order").all()
    serializer_class = StaffTaskSerializer
    search_fields = ["staff__name", "order__code", "title", "notes"]
    filterset_fields = ["staff", "order", "status"]
    allowed_roles = STAFF_ROLES + [ROLE_TECHNICIAN]

    def get_queryset(self):
        qs = super().get_queryset()
        if user_role_code(self.request.user) == ROLE_TECHNICIAN:
            return qs.filter(staff__user=self.request.user)
        return qs


class StaffAdvanceViewSet(EventOpsModelViewSet):
    queryset = StaffAdvance.objects.select_related("staff").all()
    serializer_class = StaffAdvanceSerializer
    filterset_fields = ["staff", "advance_date"]
    allowed_roles = FINANCE_ROLES

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class StaffBonusViewSet(EventOpsModelViewSet):
    queryset = StaffBonus.objects.select_related("staff").all()
    serializer_class = StaffBonusSerializer
    filterset_fields = ["staff", "bonus_date"]
    allowed_roles = FINANCE_ROLES

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class StaffDeductionViewSet(EventOpsModelViewSet):
    queryset = StaffDeduction.objects.select_related("staff").all()
    serializer_class = StaffDeductionSerializer
    filterset_fields = ["staff", "deduction_date"]
    allowed_roles = FINANCE_ROLES

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
