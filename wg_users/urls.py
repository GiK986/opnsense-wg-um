from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index_wg_users"),
    path("create/", views.create, name="create_wg_users"),

    # AllowedIpsGroup
    path("allowed_ips_group/", views.allowed_ips_group_index, name="index_allowed_ips_group"),
    path("allowed_ips_group/create/", views.allowed_ips_group_create, name="create_allowed_ips_group"),
    path("allowed_ips_group/update/<str:allowed_ips_group_id>/", views.allowed_ips_group_update, name="update_allowed_ips_group"),
    path("allowed_ips_group/delete/<str:allowed_ips_group_id>/", views.allowed_ips_group_delete, name="delete_allowed_ips_group"),
    path("calculate_allowed_ips/", views.calculate_allowed_ips, name="calculate_allowed_ips"),
]
