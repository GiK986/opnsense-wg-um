from django.urls import path
from . import views


urlpatterns = [
    path("login", views.login_user, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("register", views.register, name="register"),
    path("sample-page", views.SampleView.as_view(), name="sample-page"),
]
