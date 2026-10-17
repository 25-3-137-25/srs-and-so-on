from django.contrib.auth import views as auth_views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import dashboard, CategoryViewSet, TicketViewSet

router = DefaultRouter()
router.register(
    "categories",
    CategoryViewSet,
    basename="categories",
)
router.register(
    "tickets",
    TicketViewSet,
    basename="tickets",
)

urlpatterns = [
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="tickets/login.html",
            next_page="tickets-dashboard",
            redirect_authenticated_user=True,
        ),
        name="account-login",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="tickets/login.html",
            next_page="tickets-dashboard",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("", dashboard, name="tickets-dashboard"),
    path("api/", include(router.urls)),
]
