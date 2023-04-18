from django.shortcuts import render
from utils.api_client import ApiClient
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def dashboard(request, filter_key=None):
    api_client = ApiClient(**request.user.default_api_client.to_dict())
    clients = api_client.get_client_stats_by_filter(filter_key)
    status_count = api_client.get_client_stats_count()
    context = {
        "status_count": status_count,
        "clients": clients,
    }
    return render(request, "dashboard/dashboard.html", context)
