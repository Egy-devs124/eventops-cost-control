from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.finance.views import (
    BankAccountViewSet,
    CashboxViewSet,
    CashTransactionViewSet,
    ExpenseCategoryViewSet,
    ExpenseViewSet,
    FinancialApprovalViewSet,
    InvoiceItemViewSet,
    InvoiceViewSet,
    PaymentMethodViewSet,
    PaymentViewSet,
)


router = DefaultRouter()
router.register("payment-methods", PaymentMethodViewSet)
router.register("bank-accounts", BankAccountViewSet)
router.register("cashboxes", CashboxViewSet)
router.register("cash-transactions", CashTransactionViewSet)
router.register("expense-categories", ExpenseCategoryViewSet)
router.register("expenses", ExpenseViewSet)
router.register("invoices/items", InvoiceItemViewSet)
router.register("invoices", InvoiceViewSet)
router.register("payments", PaymentViewSet)
router.register("approvals", FinancialApprovalViewSet)

urlpatterns = [path("", include(router.urls))]
