from django.urls import path

from users.views import (
    UserView,
    login,
    signup,
    activate_user,
    forgot_password,
    change_password,
    ProfileView,
    ResidentialAddressView,
)

urlpatterns = [
    path("users", UserView.as_view(), name="users"),
    path("profile", ProfileView.as_view(), name="profile"),
    path("address", ResidentialAddressView.as_view(), name="address"),
    path("signup", signup, name="signup"),
    path(
        "activate/<str:uid>/<str:token>", activate_user, name="activate-user"
    ),
    path("login", login, name="login"),
    path("forgot-password", forgot_password, name="forgot-password"),
    path("change-password", change_password, name="change-password"),
]
