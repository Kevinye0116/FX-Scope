from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    RegisterView,
    delete_account,
    favorite_view,
    get_user_info,
    update_user_info,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("favorites/", favorite_view, name="favorites"),
    path("info/", get_user_info, name="user-info"),
    path("update/", update_user_info, name="update-user-info"),
    path("account/", delete_account, name="delete_account"),
]
