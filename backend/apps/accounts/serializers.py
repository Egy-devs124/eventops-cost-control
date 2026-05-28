from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.models import Role, UserProfile


User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ["user"]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    role_code = serializers.CharField(source="role.code", read_only=True)
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "role_code",
            "role_name",
            "language",
            "theme",
            "is_active",
            "is_staff",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        UserProfile.objects.get_or_create(user=user)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        UserProfile.objects.get_or_create(user=instance)
        return instance

    def get_role_name(self, obj):
        role = getattr(obj, "role", None)
        if not role:
            return ""
        request = self.context.get("request")
        language = ""
        if request:
            language = (request.headers.get("Accept-Language") or "").lower()
        if not language:
            language = getattr(obj, "language", "")
        return role.name_ar if str(language).startswith("ar") else role.name_en


class MeSerializer(UserSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["profile"]
