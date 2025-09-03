from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .models import User, Grocery, Item, DailyIncome
from .serializers import (
    UserSerializer,
    GrocerySerializer,
    ItemSerializer,
    DailyIncomeSerializer,
)
from neomodel import DoesNotExist
from datetime import datetime

from .permissions import IsAdmin, IsSupplierOfGrocery

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)  # Import the base view here

from .serializers import (
    CustomTokenObtainPairSerializer,  # Import your custom serializer here
)


# Add the custom token view here
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class NeomodelBaseViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    lookup_field = "uid"

    def get_object(self):
        try:
            # Use the correct lookup field 'uid'
            return self.queryset.get(uid=self.kwargs[self.lookup_field])
        except DoesNotExist:
            raise NotFound()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        # Explicitly save the instance and update the timestamp
        instance = serializer.save()
        instance.updated_at = datetime.now()
        instance.save()
        return instance

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Generic soft delete logic.
        if hasattr(instance, "soft_deleted"):
            instance.soft_deleted = True
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # Perform a hard delete for models without soft_deleted
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(NeomodelBaseViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.nodes.all()

    def destroy(self, request, *args, **kwargs):
        # Users are not soft deleted, so use the hard delete logic from the base viewset
        return super().destroy(request, *args, **kwargs)


class GroceryViewSet(NeomodelBaseViewSet):
    serializer_class = GrocerySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Grocery.nodes.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        grocery = serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        # Groceries are not soft deleted, so use the hard delete logic from the base viewset
        return super().destroy(request, *args, **kwargs)


class ItemViewSet(NeomodelBaseViewSet):
    serializer_class = ItemSerializer

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if user and user.role == "SUPPLIER":
            # Suppliers can read all items, so don't filter.
            # The soft-deleted filter should apply to both.
            return Item.nodes.filter(soft_deleted=False)
        # Admins can see all items
        return Item.nodes.filter(soft_deleted=False)

    def get_permissions(self):
        if self.action == "create":
            # A supplier can only create an item if they are assigned to a grocery
            permission_classes = [IsAuthenticated, IsSupplierOfGrocery]
        elif self.action in ["retrieve", "list"]:
            permission_classes = [IsAuthenticated]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsAdmin]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        user = getattr(request, "user", None)
        if not user or user.role != "SUPPLIER":
            raise PermissionDenied("Only suppliers can add new items.")

        try:
            # Assumes the user-to-grocery relationship is called `suppliers`
            # as per your model definition.
            user_grocery = user.suppliers.single()
        except DoesNotExist:
            raise PermissionDenied("Supplier is not linked to a grocery.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        user_grocery.items.connect(item)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class DailyIncomeViewSet(NeomodelBaseViewSet):
    serializer_class = DailyIncomeSerializer

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if user and user.role == "SUPPLIER":
            # Suppliers can only see their own income reports
            try:
                user_grocery = user.suppliers.single()
                return user_grocery.incomes.all()
            except DoesNotExist:
                return DailyIncome.nodes.none()  # Return an empty queryset
        # Admins can see all daily incomes
        return DailyIncome.nodes.all()

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated, IsSupplierOfGrocery]
        elif self.action in ["retrieve", "list"]:
            # Admins can read all, suppliers can read their own
            permission_classes = [IsAuthenticated, IsAdmin | IsSupplierOfGrocery]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsAdmin]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        user = getattr(request, "user", None)
        if not user or user.role != "SUPPLIER":
            raise PermissionDenied("Only suppliers can add new incomes.")

        try:
            user_grocery = user.suppliers.single()
        except DoesNotExist:
            raise PermissionDenied("Supplier is not linked to a grocery.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        income = serializer.save()
        user_grocery.incomes.connect(income)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
