from rest_framework.permissions import BasePermission
from .models import DailyIncome, User, Item
from neomodel import DoesNotExist


# This will be used by the authentication backend to populate the request.user
class UserFromToken(object):
    def __init__(self, email):
        try:
            self.user = User.nodes.get(email=email)
        except User.DoesNotExist:
            self.user = None

    @property
    def is_authenticated(self):
        return self.user is not None


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return user is not None and user.role == "ADMIN"


class IsSupplier(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return user is not None and user.role == "SUPPLIER"


class IsSupplierOfGrocery(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if user is None or user.role != "SUPPLIER":
            return False

        # Check if the user is linked to a grocery
        try:
            user_grocery = user.MANAGED_BY.single()
            if not user_grocery:
                return False
            # Check if the request is trying to modify a resource under their grocery
            # This requires custom logic in the view, as permission checks often happen before object retrieval.
            # We'll use this permission for the `create` and `list` methods.
            return True
        except DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        # This is for detailed views (retrieve, update, delete)
        user = getattr(request, "user", None)
        if user is None or user.role != "SUPPLIER":
            return False

        try:
            user_grocery = user.MANAGED_BY.single()
            if not user_grocery:
                return False

            # Check if the object (e.g., Item or DailyIncome) belongs to the user's grocery
            if isinstance(obj, Item):
                # Traverse the graph to find the item's grocery
                item_grocery = obj.HAS_ITEM.single()
                return item_grocery and item_grocery.id == user_grocery.id

            if isinstance(obj, DailyIncome):
                income_grocery = obj.REPORTS_INCOME.single()
                return income_grocery and income_grocery.id == user_grocery.id
        except DoesNotExist:
            return False

        return False
