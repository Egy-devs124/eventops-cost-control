from rest_framework import serializers

from apps.payroll.models import PayrollLine, PayrollPeriod


class PayrollLineSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.name", read_only=True)

    class Meta:
        model = PayrollLine
        fields = "__all__"


class PayrollPeriodSerializer(serializers.ModelSerializer):
    lines = PayrollLineSerializer(many=True, read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.username", read_only=True)

    class Meta:
        model = PayrollPeriod
        fields = "__all__"
        read_only_fields = ["approved_by", "paid_at"]
