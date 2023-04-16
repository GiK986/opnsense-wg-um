from django.shortcuts import render
from utils.api_client import ApiClient


# Create your views here.
def index(request):
    api_client = ApiClient(**request.user.default_api_client.to_dict())
    interface_clients = api_client.get_interface_clients()

    context = {
        'wg_users': interface_clients,
    }

    return render(request, "wg_users/index.html", context)
