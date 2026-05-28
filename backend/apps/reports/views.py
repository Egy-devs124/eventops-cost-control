import csv

from django.http import HttpResponse
from openpyxl import Workbook
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.constants import FINANCE_ROLES, MANAGEMENT_ROLES, OPERATIONS_ROLES, ROLE_SALES
from apps.common.permissions import RoleScopedPermission
from apps.reports.services import (
    client_balance,
    dashboard_metrics,
    driver_balance,
    profit_report,
    revenue_report,
    vendor_balance,
)


class RoleProtectedAPIView(APIView):
    permission_classes = [RoleScopedPermission]
    allowed_roles = MANAGEMENT_ROLES + FINANCE_ROLES + OPERATIONS_ROLES + [ROLE_SALES]


class DashboardView(RoleProtectedAPIView):
    def get(self, request):
        return Response(dashboard_metrics())


class RevenueReportView(RoleProtectedAPIView):
    def get(self, request):
        return Response(revenue_report())


class ProfitReportView(RoleProtectedAPIView):
    allowed_roles = MANAGEMENT_ROLES + FINANCE_ROLES

    def get(self, request):
        return Response(profit_report())


class ClientBalancesView(RoleProtectedAPIView):
    def get(self, request):
        from apps.clients.models import Client

        return Response(
            [{"id": c.id, "name": c.name, "balance": client_balance(c)} for c in Client.objects.all()]
        )


class VendorBalancesView(RoleProtectedAPIView):
    allowed_roles = MANAGEMENT_ROLES + FINANCE_ROLES

    def get(self, request):
        from apps.vendors.models import Vendor

        return Response(
            [{"id": v.id, "name": v.name, "balance": vendor_balance(v)} for v in Vendor.objects.all()]
        )


class DriverBalancesView(RoleProtectedAPIView):
    allowed_roles = MANAGEMENT_ROLES + FINANCE_ROLES

    def get(self, request):
        from apps.drivers.models import Driver

        return Response(
            [{"id": d.id, "name": d.name, "balance": driver_balance(d)} for d in Driver.objects.all()]
        )


class ExportReportView(RoleProtectedAPIView):
    def get(self, request):
        report = request.query_params.get("report", "profit")
        export_format = request.query_params.get("file_format", "csv")
        language = self.get_language(request)
        rows = self.get_rows(report)
        headers = self.get_headers(report, rows, language)
        if export_format == "xlsx":
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = self.get_report_title(report, language)[:31]
            sheet.sheet_view.rightToLeft = language == "ar"
            if rows:
                sheet.append([label for _, label in headers])
                for row in rows:
                    sheet.append([str(row.get(key, "")) for key, _ in headers])
            else:
                sheet.append([self.label("message", language)])
                sheet.append([self.label("empty", language)])
            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = f'attachment; filename="{report}-report.xlsx"'
            workbook.save(response)
            return response

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{report}-report.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)
        if rows:
            writer.writerow([label for _, label in headers])
            for row in rows:
                writer.writerow([row.get(key, "") for key, _ in headers])
        else:
            writer.writerow([self.label("message", language)])
            writer.writerow([self.label("empty", language)])
        return response

    def get_language(self, request):
        language = (request.query_params.get("lang") or request.headers.get("Accept-Language") or "en").lower()
        return "ar" if language.startswith("ar") else "en"

    def get_rows(self, report):
        if report == "profit":
            return profit_report()
        if report == "client-balances":
            from apps.clients.models import Client

            return [{"name": c.name, "balance": client_balance(c)} for c in Client.objects.all()]
        if report == "vendor-balances":
            from apps.vendors.models import Vendor

            return [{"name": v.name, "balance": vendor_balance(v)} for v in Vendor.objects.all()]
        return []

    def get_headers(self, report, rows, language):
        if report == "profit":
            keys = [
                "order_number",
                "client",
                "job_title",
                "revenue",
                "item_costs",
                "staff_costs",
                "vendor_costs",
                "driver_costs",
                "expenses",
                "total_costs",
                "profit",
                "margin_percent",
            ]
            return [(key, self.label(key, language)) for key in keys]
        if report in ["client-balances", "vendor-balances"]:
            return [("name", self.label("name", language)), ("balance", self.label("balance", language))]
        if rows:
            return [(key, self.label(key, language)) for key in rows[0].keys()]
        return []

    def get_report_title(self, report, language):
        titles = {
            "en": {
                "profit": "Profit Report",
                "client-balances": "Client Balances",
                "vendor-balances": "Vendor Balances",
            },
            "ar": {
                "profit": "تقرير الربحية",
                "client-balances": "أرصدة العملاء",
                "vendor-balances": "أرصدة الموردين",
            },
        }
        return titles[language].get(report, report.replace("-", " ").title())

    def label(self, key, language):
        labels = {
            "en": {
                "order_number": "Order Number",
                "client": "Client",
                "job_title": "Job Title",
                "revenue": "Revenue",
                "item_costs": "Item Costs",
                "staff_costs": "Staff Costs",
                "vendor_costs": "Vendor Costs",
                "driver_costs": "Driver Costs",
                "expenses": "Expenses",
                "total_costs": "Total Costs",
                "profit": "Profit",
                "margin_percent": "Margin %",
                "name": "Name",
                "balance": "Balance",
                "message": "Message",
                "empty": "No rows for selected report.",
            },
            "ar": {
                "order_number": "رقم الطلب",
                "client": "اسم العميل",
                "job_title": "عنوان الطلب",
                "revenue": "الإيرادات",
                "item_costs": "تكاليف الأصناف",
                "staff_costs": "تكاليف الفنيين",
                "vendor_costs": "تكاليف الموردين",
                "driver_costs": "تكاليف السائقين",
                "expenses": "المصروفات",
                "total_costs": "إجمالي التكاليف",
                "profit": "الربح",
                "margin_percent": "هامش الربح %",
                "name": "الاسم",
                "balance": "الرصيد",
                "message": "رسالة",
                "empty": "لا توجد بيانات للتقرير المحدد.",
            },
        }
        return labels[language].get(key, key.replace("_", " ").title())
