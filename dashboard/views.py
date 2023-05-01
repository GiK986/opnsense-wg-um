from django.shortcuts import render
from utils.api_client import ApiClient
from django.contrib.auth.decorators import login_required
from utils.decorators import api_client_required
from wg_users.models import WireguardConfig


# Create your views here.
@login_required
@api_client_required
def dashboard(request, filter_key=None):
    api_client = ApiClient(**request.user.default_api_client.to_dict())
    clients = api_client.get_client_stats_by_filter(filter_key)
    status_count = api_client.get_client_stats_count()
    status_percent = api_client.get_client_stats_percent()

    wg_user_configs = WireguardConfig.objects.all().values('wg_user_uuid')

    for client in clients:
        for wg_user_config in wg_user_configs:
            client['config'] = False
            if client['uuid'] == str(wg_user_config['wg_user_uuid']):
                client['config'] = True
                break

    context = {
        "status_count": status_count,
        "status_percent": status_percent,
        "clients": clients,
    }
    return render(request, "dashboard/dashboard.html", context)
