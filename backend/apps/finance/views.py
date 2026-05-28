from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.api import EventOpsModelViewSet
from apps.common.constants import CASHBOX_ROLES, FINANCE_ROLES, MANAGEMENT_ROLES, ROLE_SALES
from apps.finance.models import (
    BankAccount,
    CashTransaction,
    Cashbox,
    Expense,
    ExpenseCategory,
    FinancialApproval,
    Invoice,
    InvoiceItem,
    Payment,
    PaymentMethod,
)
from apps.finance.serializers import (
    BankAccountSerializer,
    CashTransactionSerializer,
    CashboxSerializer,
    ExpenseCategorySerializer,
    ExpenseSerializer,
    FinancialApprovalSerializer,
    InvoiceItemSerializer,
    InvoiceSerializer,
    PaymentMethodSerializer,
    PaymentSerializer,
)
from apps.finance.services import update_invoice_status


class PaymentMethodViewSet(EventOpsModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    search_fields = ["name", "method_type"]
    allowed_roles = FINANCE_ROLES


class BankAccountViewSet(EventOpsModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    search_fields = ["name", "bank_name", "account_number"]
    allowed_roles = FINANCE_ROLES


class CashboxViewSet(EventOpsModelViewSet):
    queryset = Cashbox.objects.all()
    serializer_class = CashboxSerializer
    search_fields = ["name", "currency"]
    allowed_roles = CASHBOX_ROLES


class CashTransactionViewSet(EventOpsModelViewSet):
    queryset = CashTransaction.objects.select_related("cashbox", "order").all()
    serializer_class = CashTransactionSerializer
    search_fields = ["cashbox__name", "description", "order__code"]
    filterset_fields = ["cashbox", "transaction_type", "transaction_date", "requires_approval"]
    allowed_roles = CASHBOX_ROLES

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ExpenseCategoryViewSet(EventOpsModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    search_fields = ["name"]
    allowed_roles = FINANCE_ROLES


class ExpenseViewSet(EventOpsModelViewSet):
    queryset = Expense.objects.select_related("category", "order", "vendor").all()
    serializer_class = ExpenseSerializer
    search_fields = ["description", "order__code", "vendor__name", "category__name"]
    filterset_fields = ["category", "order", "vendor", "expense_date", "status"]
    allowed_roles = FINANCE_ROLES

    def perform_create(self, serializer):
        category = serializer.validated_data["category"]
        amount = serializer.validated_data["amount"]
        status = "pending" if category.requires_approval_above and amount >= category.requires_approval_above else "approved"
        serializer.save(created_by=self.request.user, status=status)


class InvoiceViewSet(EventOpsModelViewSet):
    queryset = Invoice.objects.select_related("client", "order").prefetch_related("items").all()
    serializer_class = InvoiceSerializer
    search_fields = ["code", "client__name", "order__code", "notes"]
    filterset_fields = ["client", "order", "status", "issue_date", "due_date"]
    allowed_roles = FINANCE_ROLES + [ROLE_SALES]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="issue")
    def issue(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = "issued"
        invoice.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(invoice).data)


class InvoiceItemViewSet(EventOpsModelViewSet):
    queryset = InvoiceItem.objects.select_related("invoice").all()
    serializer_class = InvoiceItemSerializer
    search_fields = ["invoice__code", "description"]
    filterset_fields = ["invoice"]
    allowed_roles = FINANCE_ROLES


class PaymentViewSet(EventOpsModelViewSet):
    queryset = Payment.objects.select_related("client", "order", "invoice", "method", "cashbox", "bank_account").all()
    serializer_class = PaymentSerializer
    search_fields = ["client__name", "order__code", "invoice__code", "reference", "notes"]
    filterset_fields = ["client", "order", "invoice", "payment_date", "method", "cashbox"]
    allowed_roles = FINANCE_ROLES + [ROLE_SALES]

    def perform_create(self, serializer):
        payment = serializer.save(created_by=self.request.user)
        if payment.invoice:
            update_invoice_status(payment.invoice)


class FinancialApprovalViewSet(EventOpsModelViewSet):
    queryset = FinancialApproval.objects.select_related("requested_by", "approved_by").all()
    serializer_class = FinancialApprovalSerializer
    search_fields = ["approval_type", "reason", "content_type", "object_id"]
    filterset_fields = ["approval_type", "status"]
    allowed_roles = MANAGEMENT_ROLES + FINANCE_ROLES

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        approval = self.get_object()
        approval.status = "approved"
        approval.approved_by = request.user
        approval.save(update_fields=["status", "approved_by", "updated_at"])
        return Response(self.get_serializer(approval).data)
