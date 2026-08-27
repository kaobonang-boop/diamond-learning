from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.DiamondLoginView.as_view(), name="login"),
    path("logout/", views.DiamondLogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.edit_profile, name="edit_profile"),

    path("password/change/", views.DiamondPasswordChangeView.as_view(), name="password_change"),
    path("password/change/done/", views.DiamondPasswordChangeDoneView.as_view(), name="password_change_done"),
    path("password/reset/", views.DiamondPasswordResetView.as_view(), name="password_reset"),
    path("password/reset/done/", views.DiamondPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password/reset/confirm/<uidb64>/<token>/", views.DiamondPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password/reset/complete/", views.DiamondPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
