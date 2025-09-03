import bcrypt
from rest_framework import serializers
from .models import User, Grocery, Item, DailyIncome
from neomodel import db, DoesNotExist
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    name = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)
    role = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        password = validated_data.pop("password").encode("utf-8")
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")
        user = User(**validated_data, password=hashed_password)
        user.save()
        return user

    def update(self, instance, validated_data):
        # Update user fields
        instance.email = validated_data.get("email", instance.email)
        instance.name = validated_data.get("name", instance.name)
        if "password" in validated_data:
            password = validated_data["password"].encode("utf-8")
            instance.password = bcrypt.hashpw(password, bcrypt.gensalt()).decode(
                "utf-8"
            )

        instance.save()
        return instance


class GrocerySerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        grocery = Grocery(**validated_data)
        grocery.save()
        return grocery

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.location = validated_data.get("location", instance.location)
        instance.save()
        return instance


class ItemSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255)
    item_type = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255)
    soft_deleted = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        item = Item(**validated_data)
        item.save()
        return item

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.item_type = validated_data.get("item_type", instance.item_type)
        instance.location = validated_data.get("location", instance.location)
        instance.save()
        return instance


class DailyIncomeSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    amount = serializers.IntegerField()
    date = serializers.DateField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        income = DailyIncome(**validated_data)
        income.save()
        return income

    def update(self, instance, validated_data):
        instance.amount = validated_data.get("amount", instance.amount)
        instance.date = validated_data.get("date", instance.date)
        instance.save()
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["role"] = user.role
        return token
