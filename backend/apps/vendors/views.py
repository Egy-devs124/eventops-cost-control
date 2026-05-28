from apps.common.api import EventOpsModelViewSet
from apps.common.constants import FINANCE_ROLES, MANAGEMENT_ROLES, OPERATIONS_ROLES
from apps.vendors.models import Vendor, VendorPayment, VendorTransaction
from apps.vendors.serializers import VendorPaymentSerializer, VendorSerializer, VendorTransactionSerializer


VENDOR_ROLES = list(set(MANAGEMENT_ROLES + OPERATIONS_ROLES + FINANCE_ROLES))


class VendorViewSet(EventOpsModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    search_fields = ["name", "service_type", "phone", "email"]
    filterset_fields = ["is_active", "service_type"]
    allowed_roles = VENDOR_ROLES


class VendorTransactionViewSet(EventOpsModelViewSet):
    queryset = VendorTransaction.objects.select_related("vendor", "order").all()
    serializer_class = VendorTransactionSerializer
    search_fields = ["vendor__name", "description", "order__code"]
    filterset_fields = ["vendor", "order", "transaction_type", "transaction_date"]
    allowed_roles = FINANCE_ROLES

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class VendorPaymentViewSet(EventOpsModelViewSet):
    queryset = VendorPayment.objects.select_related("vendor", "order").all()
    serializer_class = VendorPaymentSerializer
    search_fields = ["vendor__name", "reference", "order__code"]
    filterset_fields = ["vendor", "order", "payment_date", "method"]
    allowed_roles = FINANCE_ROLES

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
