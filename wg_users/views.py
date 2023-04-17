import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from utils.api_client import ApiClient
from utils.pywgtools import wg_allowed_ips
from .forms import AllowedIpsGroupForm


# Create your views here.
def index(request):
    api_client = ApiClient(**request.user.default_api_client.to_dict())
    interface_clients = api_client.get_interface_clients()

    context = {
        'wg_users': interface_clients,
    }

    return render(request, "wg_users/index.html", context)


def create(request):
    api_client = ApiClient(**request.user.default_api_client.to_dict())
    interfaces = api_client.get_interfaces()
    allowed_ips_groups = request.user.allowedipsgroup_set.all().values('id', 'group_name')
    context = {
        'interfaces': interfaces,
        'allowed_ips_groups': allowed_ips_groups,
    }
    return render(request, "wg_users/create.html", context)


# AllowedIpsGroup
def allowed_ips_group_index(request):
    context = {
        'allowed_ips_groups': request.user.allowedipsgroup_set.all(),
    }
    return render(request, "allowed_ips_group/index.html", context)


def allowed_ips_group_create(request):
    form = AllowedIpsGroupForm(request.user)
    context = {"form": form, "button_text": "Create"}
    if request.method == "POST":
        form = AllowedIpsGroupForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect("index_allowed_ips_group")

    return render(request, "allowed_ips_group/create.html", context)


def allowed_ips_group_update(request, allowed_ips_group_id):
    allowed_ips_group = request.user.allowedipsgroup_set.get(id=allowed_ips_group_id)
    form = AllowedIpsGroupForm(request.user, instance=allowed_ips_group)
    context = {"form": form, "button_text": "Update"}
    if request.method == "POST":
        form = AllowedIpsGroupForm(request.user, request.POST, instance=allowed_ips_group)
        if form.is_valid():
            form.save()
            return redirect("index_allowed_ips_group")

    return render(request, "allowed_ips_group/create.html", context)


def allowed_ips_group_delete(request, allowed_ips_group_id):
    allowed_ips_group = request.user.allowedipsgroup_set.get(id=allowed_ips_group_id)
    if request.method == "POST":
        allowed_ips_group.delete()
        return redirect("index_allowed_ips_group")

    context = {"allowed_ips_group": allowed_ips_group}
    return render(request, "allowed_ips_group/delete.html", context)


@csrf_exempt
def calculate_allowed_ips(request):
    allowed_ips_calculated = None
    if request.method == 'POST':
        data = json.loads(request.body)
        allowed_ips = data.get('allowed_ips')
        disallowed_ips = data.get('disallowed_ips')
        allowed_ips_calculated = wg_allowed_ips.calculate_allowed_ips(allowed_ips, disallowed_ips)

    return JsonResponse({'allowed_ips_calculated': allowed_ips_calculated})
