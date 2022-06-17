from users.models import User, Profile, ResidentialAddress
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "email")


class SignUpSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "email", "password")


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
