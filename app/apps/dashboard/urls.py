from django.urls import path
from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("filter/<str:filter_key>", views.DashboardView.as_view(), name="dashboard_filter"),
]
