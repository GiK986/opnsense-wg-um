from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index_api_clients"),
    path("create", views.create, name="create_api_client"),
    path("test_connection", views.test_connection, name="test_connection_api_client"),
    path("update/<str:pk>", views.update, name="update_api_client"),
    path("delete/<str:pk>", views.delete, name="delete_api_client"),
    path("set_default/<str:pk>", views.set_default, name="set_default_api_client"),
]