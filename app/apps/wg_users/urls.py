from django.urls import path
from . import views


urlpatterns = [
    path("", views.WGUsersIndexView.as_view(), name="index_wg_users"),
    path("create/", views.WGUsersCreateView.as_view(), name="create_wg_users"),
    path("update/<str:wg_user_uuid>/", views.update, name="update_wg_users"),
    path("delete/<str:wg_user_uuid>/", views.delete, name="delete_wg_users"),
    path("reconfiguration/<str:wg_user_uuid>/", views.reconfiguration, name="reconfiguration_wg_users"),
    path("download/<str:wg_user_uuid>/", views.download, name="download_wg_users"),
    path("generate_qrcode/<str:wg_user_uuid>/", views.generate_qrcode, name="generate_qrcode_wg_users"),
    path("download_qrcode/<str:wg_user_uuid>/", views.download_qrcode, name="download_qrcode_wg_users"),
    path("share_qrcode_link/<str:wg_user_uuid>/", views.share_qrcode_link, name="share_qrcode_link_wg_users"),
    path("get_qrcode_link/", views.get_qrcode_link, name="get_qrcode_link_wg_users"),
    path("search/<str:q>/", views.search, name="search_wg_users"),
    path("send_email/<str:wg_user_uuid>/", views.send_email, name="send_email_wg_users"),

    # AllowedIpsGroup
    path("allowed_ips_group/", views.AllowedIPsGroupIndexView.as_view(), name="index_allowed_ips_group"),
    path("allowed_ips_group/create/", views.AllowedIPsGroupCreateView.as_view(), name="create_allowed_ips_group"),
    path("allowed_ips_group/update/<str:pk>/", views.AllowedIPsGroupUpdateView.as_view(), name="update_allowed_ips_group"),
    path("allowed_ips_group/delete/<str:pk>/", views.AllowedIPsGroupDeleteView.as_view(), name="delete_allowed_ips_group"),
    path("calculate_allowed_ips/", views.calculate_allowed_ips, name="calculate_allowed_ips"),
]
