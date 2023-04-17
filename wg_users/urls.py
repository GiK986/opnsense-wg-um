from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index_wg_users"),
    path("create/", views.create, name="create_wg_users"),
]