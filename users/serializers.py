from users.models import User, Profile, ResidentialAddress
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.name)
        instance.save()
        return instance

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

    def update(self, instance, validated_data):
        instance.middle_name = validated_data.get(
            "middle_name", instance.middle_name
        )
        instance.last_name = validated_data.get(
            "last_name", instance.last_name
        )
        instance.dob = validated_data.get("dob", instance.dob)
        instance.nationality = validated_data.get(
            "nationality", instance.nationality
        )
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.save()
        return instance


class ResidentialAddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ResidentialAddress
        fields = ("user_id", "country", "city", "state", "zip")

    user_id = serializers.UUIDField()

    def update(self, instance, validated_data):
        instance.country = validated_data.get("country", instance.country)
        instance.city = validated_data.get("city", instance.city)
        instance.state = validated_data.get("state", instance.state)
        instance.zip = validated_data.get("zip", instance.zip)
        instance.save()
        return instance
