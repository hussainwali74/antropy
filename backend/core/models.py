from django.db import models

# Create your models here.
from neomodel import IntegerProperty, DateProperty
from neomodel import (
    StructuredNode,
    StringProperty,
    EmailProperty,
    DateTimeProperty,
    RelationshipTo,
    BooleanProperty,
)


class User(StructuredNode):
    email = EmailProperty(unique_index=True)
    name = StringProperty(required=True)
    password = StringProperty(required=True)
    role = StringProperty(choices={"ADMIN": "Admin", "SUPPLIER": "Supplier"})
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)


class Grocery(StructuredNode):
    name = StringProperty(unique_index=True)
    location = StringProperty()
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)

    # Relationships
    suppliers = RelationshipTo("User", "MANAGED_BY")
    items = RelationshipTo("Item", "HAS_ITEM")
    incomes = RelationshipTo("DailyIncome", "REPORTS_INCOME")


class Item(StructuredNode):
    name = StringProperty()
    item_type = StringProperty()  # `item_type` is a Python keyword.
    location = StringProperty()
    soft_deleted = BooleanProperty(default=False)
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)


class DailyIncome(StructuredNode):
    amount = IntegerProperty()
    date = DateProperty()
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)
