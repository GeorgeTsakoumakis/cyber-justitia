from django.urls import path
from . import views
from .tests import test_error_handlers

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("codeofconduct", views.codeofconduct, name="codeofconduct"),
<<<<<<< HEAD
    # path("profile/", views.profile, name="profile"),

=======
    path("dashboard/", views.dashboard, name="dashboard"),
>>>>>>> 3eeadd4 (dashboard fixes)


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
