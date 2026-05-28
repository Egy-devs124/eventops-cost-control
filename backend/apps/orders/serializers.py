from rest_framework import serializers

from apps.orders.models import (
    JobDriverAssignment,
    JobSchedule,
    JobStaffAssignment,
    JobTask,
    JobVendorAssignment,
    Order,
    OrderItem,
    OrderStatusHistory,
)


class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_code = serializers.CharField(source="item.sku", read_only=True)
    category_name = serializers.CharField(source="item.category.name", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.username", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = "__all__"
        read_only_fields = ["changed_by"]


class JobScheduleSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.code", read_only=True)

    class Meta:
        model = JobSchedule
        fields = "__all__"


class JobTaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source="assigned_to.name", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)

    class Meta:
        model = JobTask
        fields = "__all__"


class JobStaffAssignmentSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.name", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)

    class Meta:
        model = JobStaffAssignment
        fields = "__all__"


class JobVendorAssignmentSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)

    class Meta:
        model = JobVendorAssignment
        fields = "__all__"


class JobDriverAssignmentSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source="driver.name", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)

    class Meta:
        model = JobDriverAssignment
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    order_number = serializers.CharField(source="code", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    profitability = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["created_by"]

    def validate(self, attrs):
        start_at = attrs.get("start_at", getattr(self.instance, "start_at", None))
        end_at = attrs.get("end_at", getattr(self.instance, "end_at", None))
        if start_at and end_at and end_at <= start_at:
            raise serializers.ValidationError({"end_at": "End date must be after start date."})
        return attrs

    def get_profitability(self, obj):
        request = self.context.get("request")
        role = getattr(getattr(request, "user", None), "role", None)
        if not (getattr(role, "can_view_profit", False) or getattr(request.user, "is_superuser", False)):
            return None
        from apps.orders.services import calculate_order_profit

        return calculate_order_profit(obj)
