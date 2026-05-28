from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.finance.views import CashboxViewSet, ExpenseViewSet, InvoiceViewSet, PaymentViewSet


payment_list = PaymentViewSet.as_view({"get": "list", "post": "create"})
payment_detail = PaymentViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})
expense_list = ExpenseViewSet.as_view({"get": "list", "post": "create"})
expense_detail = ExpenseViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})
cashbox_list = CashboxViewSet.as_view({"get": "list", "post": "create"})
cashbox_detail = CashboxViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})
invoice_list = InvoiceViewSet.as_view({"get": "list", "post": "create"})
invoice_detail = InvoiceViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/lookups/", include("apps.common.urls")),
    path("api/clients/", include("apps.clients.urls")),
    path("api/items/", include("apps.inventory.urls")),
    path("api/vendors/", include("apps.vendors.urls")),
    path("api/drivers/", include("apps.drivers.urls")),
    path("api/staff/", include("apps.staff.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/quotations/", include("apps.quotations.urls")),
    path("api/finance/", include("apps.finance.urls")),
    path("api/payments/", payment_list, name="payment-list-alias"),
    path("api/payments/<int:pk>/", payment_detail, name="payment-detail-alias"),
    path("api/expenses/", expense_list, name="expense-list-alias"),
    path("api/expenses/<int:pk>/", expense_detail, name="expense-detail-alias"),
    path("api/cashboxes/", cashbox_list, name="cashbox-list-alias"),
    path("api/cashboxes/<int:pk>/", cashbox_detail, name="cashbox-detail-alias"),
    path("api/invoices/", invoice_list, name="invoice-list-alias"),
    path("api/invoices/<int:pk>/", invoice_detail, name="invoice-detail-alias"),
    path("api/payroll/", include("apps.payroll.urls")),
    path("api/reports/", include("apps.reports.urls")),
    path("api/attachments/", include("apps.attachments.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/audit/", include("apps.audit.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
