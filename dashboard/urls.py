from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("filter/<str:filter_key>", views.dashboard, name="dashboard_filter"),
]
