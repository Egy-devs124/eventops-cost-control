from rest_framework import serializers

from apps.inventory.models import (
    DamageReport,
    InventoryTransaction,
    Item,
    ItemCategory,
    ItemReservation,
    ItemReturn,
    MaintenanceRecord,
)


class ItemCategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = ItemCategory
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Item
        fields = "__all__"


class InventoryTransactionSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = "__all__"
        read_only_fields = ["created_by"]


class ItemReservationSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    order_code = serializers.CharField(source="order.code", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)

    class Meta:
        model = ItemReservation
        fields = "__all__"


class ItemReturnSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="reservation.item.name", read_only=True)
    order_number = serializers.CharField(source="reservation.order.code", read_only=True)
    received_by_name = serializers.CharField(source="received_by.username", read_only=True)

    class Meta:
        model = ItemReturn
        fields = "__all__"
        read_only_fields = ["received_by"]


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = "__all__"


class DamageReportSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)

    class Meta:
        model = DamageReport
        fields = "__all__"
