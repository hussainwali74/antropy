from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.views import (
    UserViewSet,
    GroceryViewSet,
    ItemViewSet,
    DailyIncomeViewSet,
    CustomTokenObtainPairView,
)

# Create a router to automatically handle URL patterns for our viewsets
router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"groceries", GroceryViewSet, basename="grocery")
router.register(r"items", ItemViewSet, basename="item")
router.register(r"daily-incomes", DailyIncomeViewSet, basename="daily-income")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
