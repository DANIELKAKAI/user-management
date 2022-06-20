from users.models import User, Profile, ResidentialAddress
from rest_framework import serializers
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "email")


class SignUpSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "email", "password")

    def validate(self, data):
        user = User(**data)
        password = data.get("password")
        errors = dict()
        try:
            validators.validate_password(password=password, user=user)
        except ValidationError as e:
            errors["password"] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)
        return super(SignUpSerializer, self).validate(data)

    def create(self, validated_data):
        password = validated_data["password"]
        instance = self.Meta.model(**validated_data)
        instance.set_password(password)
        instance.save()
        return instance


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "user_id",
            "middle_name",
            "last_name",
            "dob",
            "nationality",
            "phone_number",
        )

    user_id = serializers.UUIDField()


class ResidentialAddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ResidentialAddress
        fields = ("user_id", "country", "city", "state", "zip")

    user_id = serializers.UUIDField()
