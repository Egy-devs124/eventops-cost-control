from decimal import Decimal

from apps.audit.models import AuditLog


def clean_value(value):
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "pk"):
        return value.pk
    return value


def log_action(user, instance, action, changes=None):
    safe_changes = {key: clean_value(value) for key, value in (changes or {}).items()}
    return AuditLog.objects.create(
        action=action,
        user=user if getattr(user, "is_authenticated", False) else None,
        model_name=instance._meta.label,
        object_id=str(instance.pk),
        changes=safe_changes,
    )
