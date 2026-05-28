from rest_framework import serializers

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


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = "__all__"


class CashboxSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Cashbox
        fields = "__all__"

    def get_balance(self, obj):
        from apps.finance.services import cashbox_balance

        return cashbox_balance(obj)


class CashTransactionSerializer(serializers.ModelSerializer):
    cashbox_name = serializers.CharField(source="cashbox.name", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.username", read_only=True)

    class Meta:
        model = CashTransaction
        fields = "__all__"
        read_only_fields = ["created_by", "approved_by"]


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = "__all__"


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    expense_category_name = serializers.CharField(source="category.name", read_only=True)
    order_code = serializers.CharField(source="order.code", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.username", read_only=True)

    class Meta:
        model = Expense
        fields = "__all__"
        read_only_fields = ["created_by", "approved_by"]


class InvoiceItemSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source="invoice.code", read_only=True)

    class Meta:
        model = InvoiceItem
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    order_code = serializers.CharField(source="order.code", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)
    invoice_number = serializers.CharField(source="code", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    paid_amount = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ["created_by"]

    def get_paid_amount(self, obj):
        from apps.finance.services import invoice_paid_amount

        return invoice_paid_amount(obj)

    def get_balance(self, obj):
        return obj.total_amount - self.get_paid_amount(obj)


class PaymentSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    order_code = serializers.CharField(source="order.code", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)
    invoice_code = serializers.CharField(source="invoice.code", read_only=True)
    invoice_number = serializers.CharField(source="invoice.code", read_only=True)
    payment_method_name = serializers.CharField(source="method.name", read_only=True)
    cashbox_name = serializers.CharField(source="cashbox.name", read_only=True)
    bank_account_name = serializers.CharField(source="bank_account.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["created_by"]


class FinancialApprovalSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source="requested_by.username", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.username", read_only=True)

    class Meta:
        model = FinancialApproval
        fields = "__all__"
        read_only_fields = ["requested_by", "approved_by"]
