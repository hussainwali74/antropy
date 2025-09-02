import bcrypt
from rest_framework import serializers
from .models import User, Grocery, Item, DailyIncome
from neomodel import db, DoesNotExist


class UserSerializer(serializers.Serializer):
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


class GrocerySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        grocery = Grocery(**validated_data)
        grocery.save()
        return grocery


class ItemSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
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


class DailyIncomeSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    amount = serializers.IntegerField()
    date = serializers.DateField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        income = DailyIncome(**validated_data)
        income.save()
        return income
