from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("<str:filter_key>", views.dashboard, name="dashboard"),
]
