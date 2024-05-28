from django.urls import path
from . import views
from .tests import test_error_handlers

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("codeofconduct", views.codeofconduct, name="codeofconduct"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("update_details/", views.update_details, name="update_details"),
    path("update_description/", views.update_description, name="update_description"),
    path("update_flair/", views.update_flair, name="update_flair"),
    path("update_education/", views.update_education, name="update_education"),
    path("update_employments/", views.update_employments, name="update_employments"),
    path(
        "400/", test_error_handlers.TestCustomErrorHandlers.custom_400_view, name="400"
    ),
    path(
        "403/", test_error_handlers.TestCustomErrorHandlers.custom_403_view, name="403"
    ),
    path(
        "500/", test_error_handlers.TestCustomErrorHandlers.custom_500_view, name="500"
    ),
    path(
        "503/", test_error_handlers.TestCustomErrorHandlers.custom_503_view, name="503"
    ),
]
