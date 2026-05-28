from rest_framework import serializers

from apps.drivers.models import Driver, DriverPayment, DriverTrip


class DriverSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Driver
        fields = "__all__"

    def get_balance(self, obj):
        from apps.reports.services import driver_balance

        return driver_balance(obj)


class DriverTripSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source="driver.name", read_only=True)
    order_code = serializers.CharField(source="order.code", read_only=True)
    order_number = serializers.CharField(source="order.code", read_only=True)

    class Meta:
        model = DriverTrip
        fields = "__all__"


class DriverPaymentSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source="driver.name", read_only=True)
    trip_label = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    def get_trip_label(self, obj):
        if not obj.trip:
            return ""
        order_code = obj.trip.order.code if obj.trip.order else "No order"
        return f"{order_code} - {obj.trip.pickup_location} to {obj.trip.dropoff_location}"

    class Meta:
        model = DriverPayment
        fields = "__all__"
        read_only_fields = ["created_by"]
