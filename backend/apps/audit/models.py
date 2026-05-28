from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    action = models.CharField(max_length=20, choices=[("create", "Create"), ("update", "Update"), ("delete", "Delete")])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    model_name = models.CharField(max_length=120, db_index=True)
    object_id = models.CharField(max_length=120, db_index=True)
    changes = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} {self.model_name} #{self.object_id}"
