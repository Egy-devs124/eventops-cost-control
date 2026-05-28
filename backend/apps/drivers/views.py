from apps.common.api import EventOpsModelViewSet
from apps.common.constants import FINANCE_ROLES, MANAGEMENT_ROLES, OPERATIONS_ROLES, ROLE_DRIVER
from apps.common.permissions import user_role_code
from apps.drivers.models import Driver, DriverPayment, DriverTrip
from apps.drivers.serializers import DriverPaymentSerializer, DriverSerializer, DriverTripSerializer


DRIVER_MGMT_ROLES = list(set(MANAGEMENT_ROLES + OPERATIONS_ROLES + FINANCE_ROLES))


class DriverViewSet(EventOpsModelViewSet):
    queryset = Driver.objects.select_related("user").all()
    serializer_class = DriverSerializer
    search_fields = ["name", "phone", "vehicle_plate", "license_number"]
    allowed_roles = DRIVER_MGMT_ROLES


class DriverTripViewSet(EventOpsModelViewSet):
    queryset = DriverTrip.objects.select_related("driver", "driver__user", "order").all()
    serializer_class = DriverTripSerializer
    search_fields = ["driver__name", "order__code", "pickup_location", "dropoff_location"]
    filterset_fields = ["driver", "order", "status", "scheduled_at"]
    allowed_roles = DRIVER_MGMT_ROLES + [ROLE_DRIVER]

    def get_queryset(self):
        qs = super().get_queryset()
        if user_role_code(self.request.user) == ROLE_DRIVER:
            return qs.filter(driver__user=self.request.user)
        return qs


class DriverPaymentViewSet(EventOpsModelViewSet):
    queryset = DriverPayment.objects.select_related("driver", "trip").all()
    serializer_class = DriverPaymentSerializer
    search_fields = ["driver__name", "reference"]
    filterset_fields = ["driver", "trip", "payment_date", "method"]
    allowed_roles = FINANCE_ROLES

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
