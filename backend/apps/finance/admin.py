from django.contrib import admin

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


admin.site.register(PaymentMethod)
admin.site.register(BankAccount)
admin.site.register(Cashbox)
admin.site.register(CashTransaction)
admin.site.register(ExpenseCategory)
admin.site.register(Expense)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Payment)
admin.site.register(FinancialApproval)
