from rest_framework import serializers

from apps.quotations.models import Quotation, QuotationItem


class QuotationItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_code = serializers.CharField(source="item.sku", read_only=True)
    quotation_number = serializers.CharField(source="quotation.code", read_only=True)

    class Meta:
        model = QuotationItem
        fields = "__all__"


class QuotationSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    quotation_number = serializers.CharField(source="code", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    items = QuotationItemSerializer(many=True, read_only=True)

    class Meta:
        model = Quotation
        fields = "__all__"
        read_only_fields = ["created_by"]
