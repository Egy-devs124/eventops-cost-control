from rest_framework import serializers

from apps.clients.models import Client, ClientBalanceSnapshot, ClientContact


class ClientContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientContact
        fields = "__all__"


class ClientBalanceSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientBalanceSnapshot
        fields = "__all__"


class ClientSerializer(serializers.ModelSerializer):
    contacts = ClientContactSerializer(many=True, read_only=True)
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = ["created_by"]

    def get_balance(self, obj):
        from apps.reports.services import client_balance

        return client_balance(obj)
