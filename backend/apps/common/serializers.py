from rest_framework import serializers


class ChoiceLabelField(serializers.Field):
    def to_representation(self, value):
        if hasattr(self.parent.instance, f"get_{self.field_name}_display"):
            return getattr(self.parent.instance, f"get_{self.field_name}_display")()
        return value

    def to_internal_value(self, data):
        return data
