from django.urls import path

from apps.reports.views import (
    ClientBalancesView,
    DashboardView,
    DriverBalancesView,
    ExportReportView,
    ProfitReportView,
    RevenueReportView,
    VendorBalancesView,
)


urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard-report"),
    path("revenue/", RevenueReportView.as_view(), name="revenue-report"),
    path("profit/", ProfitReportView.as_view(), name="profit-report"),
    path("client-balances/", ClientBalancesView.as_view(), name="client-balances"),
    path("vendor-balances/", VendorBalancesView.as_view(), name="vendor-balances"),
    path("driver-balances/", DriverBalancesView.as_view(), name="driver-balances"),
    path("export/", ExportReportView.as_view(), name="export-report"),
]
