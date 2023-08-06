from django.urls import path
from . import views


urlpatterns = [
    path("", views.WGUsersIndexView.as_view(), name="index_wg_users"),
    path("create/", views.WGUsersCreateView.as_view(), name="create_wg_users"),
    path("update/<str:wg_user_uuid>/", views.WGUsersUpdateView.as_view(), name="update_wg_users"),

    path("download/<str:wg_user_uuid>/", views.DownloadWireguardConfigFileView.as_view(), name="download_wg_users"),
    path("generated_qrcode/<str:wg_user_uuid>/", views.get_generated_qrcode, name="generated_qrcode_wg_users"),
    path("share_qrcode_link/<str:wg_user_uuid>/", views.ShareQrCodeLinkView.as_view(), name="share_qrcode_link_wg_users"),

    # AllowedIpsGroup
    path("allowed_ips_group/", views.AllowedIPsGroupIndexView.as_view(), name="index_allowed_ips_group"),
    path("allowed_ips_group/create/", views.AllowedIPsGroupCreateView.as_view(), name="create_allowed_ips_group"),
    path("allowed_ips_group/update/<str:pk>/", views.AllowedIPsGroupUpdateView.as_view(), name="update_allowed_ips_group"),
    path("allowed_ips_group/delete/<str:pk>/", views.AllowedIPsGroupDeleteView.as_view(), name="delete_allowed_ips_group"),
]
