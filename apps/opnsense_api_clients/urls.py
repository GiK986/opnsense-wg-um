from django.urls import path
from . import views


urlpatterns = [
    path("", views.OpnSenseApiClientIndexView.as_view(), name="index_api_clients"),
    path("create", views.OpnSenseApiClientCreateView.as_view(), name="create_api_client"),
    path("update/<str:pk>", views.OpnSenseApiClientUpdateView.as_view(), name="update_api_client"),
    path("delete/<str:pk>", views.DeleteView.as_view(), name="delete_api_client"),
    path("test_connection", views.test_connection, name="test_connection_api_client"),
    path("set_default/<str:pk>", views.set_default, name="set_default_api_client"),
]