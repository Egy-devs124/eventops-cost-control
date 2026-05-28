from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.constants import ALL_ROLES
from apps.common.models import TimeStampedModel


class Role(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True, choices=[(r, r) for r in ALL_ROLES])
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    can_view_profit = models.BooleanField(default=False)
    can_view_payroll = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)
    is_system = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.name_en


class User(AbstractUser):
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=2, default="en", choices=[("en", "English"), ("ar", "Arabic")])
    theme = models.CharField(max_length=10, default="light", choices=[("light", "Light"), ("dark", "Dark")])


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    job_title = models.CharField(max_length=120, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    preferred_language = models.CharField(max_length=2, default="en")
    preferred_theme = models.CharField(max_length=10, default="light")
    notification_email = models.BooleanField(default=True)
    notification_in_app = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} profile"
