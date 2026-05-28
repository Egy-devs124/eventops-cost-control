from rest_framework import serializers

from apps.staff.models import StaffAdvance, StaffBonus, StaffDeduction, StaffProfile, StaffTask


class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = "__all__"


class StaffTaskSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.name", read_only=True)
    order_code = serializers.CharField(source="order.code", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)

    class Meta:
        model = StaffTask
        fields = "__all__"


class StaffAdvanceSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = StaffAdvance
        fields = "__all__"
        read_only_fields = ["created_by"]


class StaffBonusSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = StaffBonus
        fields = "__all__"
        read_only_fields = ["created_by"]


class StaffDeductionSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = StaffDeduction
        fields = "__all__"
        read_only_fields = ["created_by"]
