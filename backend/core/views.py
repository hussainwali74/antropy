from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from .models import User, Grocery, Item, DailyIncome
from .serializers import (
    UserSerializer,
    GrocerySerializer,
    ItemSerializer,
    DailyIncomeSerializer,
)
from neomodel import DoesNotExist

from .permissions import IsAdmin, IsSupplier, IsSupplierOfGrocery


# Base viewset for neomodel nodes
class NeomodelBaseViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    lookup_field = "id"

    def get_object(self):
        try:
            return self.queryset.get(id=self.kwargs[self.lookup_field])
        except DoesNotExist:
            raise NotFound()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        # Soft delete logic
        instance.soft_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(NeomodelBaseViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.nodes.all()


class GroceryViewSet(NeomodelBaseViewSet):
    serializer_class = GrocerySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Grocery.nodes.all()

    # You'll need to override the create method to link the admin
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        grocery = serializer.save()

        # Link the admin user to the new grocery (optional, but good for tracking)
        # request.user.MANAGED.connect(grocery)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class ItemViewSet(NeomodelBaseViewSet):
    serializer_class = ItemSerializer

    def get_queryset(self):
        # A supplier can only see items from their own grocery
        user = getattr(self.request, "user", None)
        if user and user.role == "SUPPLIER":
            grocery = user.MANAGED_BY.single()
            if grocery:
                return grocery.items.all()
        # Admin can see all items
        return Item.nodes.filter(soft_deleted=False)

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated, IsSupplierOfGrocery]
        elif self.action in ["retrieve", "list"]:
            permission_classes = [IsAuthenticated]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsAdmin]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        # A supplier can only add items to their grocery
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()

        user = getattr(request, "user", None)
        grocery = user.MANAGED_BY.single()
        grocery.items.connect(item)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class DailyIncomeViewSet(NeomodelBaseViewSet):
    serializer_class = DailyIncomeSerializer

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if user and user.role == "SUPPLIER":
            grocery = user.MANAGED_BY.single()
            return grocery.incomes.all()
        # Admin can see all daily incomes
        return DailyIncome.nodes.all()

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated, IsSupplierOfGrocery]
        elif self.action in ["retrieve", "list"]:
            permission_classes = [IsAuthenticated, IsAdmin | IsSupplier]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        # A supplier can only add income for their grocery
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        income = serializer.save()

        user = getattr(request, "user", None)
        grocery = user.MANAGED_BY.single()
        grocery.incomes.connect(income)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
