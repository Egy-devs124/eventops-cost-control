from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import Role, User, UserProfile


admin.site.register(User, UserAdmin)
admin.site.register(Role)
admin.site.register(UserProfile)
