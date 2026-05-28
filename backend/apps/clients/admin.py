from django.contrib import admin

from apps.clients.models import Client, ClientBalanceSnapshot, ClientContact


admin.site.register(Client)
admin.site.register(ClientContact)
admin.site.register(ClientBalanceSnapshot)
