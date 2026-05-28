from rest_framework import serializers

from apps.vendors.models import Vendor, VendorPayment, VendorTransaction


class VendorSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = "__all__"

    def get_balance(self, obj):
        from apps.reports.services import vendor_balance

        return vendor_balance(obj)


class VendorTransactionSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = VendorTransaction
        fields = "__all__"
        read_only_fields = ["created_by"]


class VendorPaymentSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = VendorPayment
        fields = "__all__"
        read_only_fields = ["created_by"]
