from django.urls import path
from . import views


urlpatterns = [
    path("search/<str:q>/", views.SearchAPIView.as_view(), name="search_wg_users"),
    path("calculate_allowed_ips/", views.CalculateAllowedIPsAPIView.as_view(), name="calculate_allowed_ips"),
    path("send_email/<str:wg_user_uuid>/", views.SendEmailAPIView.as_view(), name="send_email_wg_users"),
    path("opnsense_api_clients/test_connection/", views.OPNsenseAPIClientTestConnectionAPIView.as_view(), name="test_connection_api_client"),
    path("reconfiguration/<str:wg_user_uuid>/", views.ReconfigurationWgUserAPIView.as_view(), name="reconfiguration_wg_users"),
    path("delete_wg_user/<str:wg_user_uuid>/", views.DeleteWgUserAPIView.as_view(), name="delete_wg_users"),
]
