import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.http import HttpResponse
from utils.api_client import ApiClient
from utils.pywgtools import wg_allowed_ips
from utils.pywgtools.wgtools import genkey, pubkey
from .forms import AllowedIpsGroupForm
from .models import WireguardConfig
from django.contrib import messages


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

    if request.method == "POST":
        interface = request.POST.get('interface')
        allowed_ips_group = request.POST.get('allowed_ips_group')
        prefix_users = request.POST.get('prefix_users')
        keepalive = int(request.POST.get('keepalive'))
        client_count = int(request.POST.get('client_count'))
        server_endpoint = request.user.default_api_client.endpoint_url
        allowed_ips = request.user.allowedipsgroup_set.get(id=allowed_ips_group).allowed_ips_calculated

        server_config = api_client.get_server_config(interface)
        hosts_iterator = api_client.get_hosts_iterator(interface)

        added_clients = []
        for _ in range(client_count):

            private_key = genkey()
            public_key = pubkey(private_key)
            available_host = str(next(hosts_iterator))
            name = f'{prefix_users}_{available_host.split(".")[-1]}'

            wg_user_uuid = api_client.add_client(name, public_key, available_host)
            added_clients.append(wg_user_uuid)

            wireguard_config = WireguardConfig(
                wg_user_uuid=wg_user_uuid,
                name=name,
                address=available_host,
                private_key=private_key,
                public_key=public_key,
                server_public_key=server_config['pubkey'],
                server_endpoint=server_endpoint,
                server_endpoint_port=server_config['port'],
                server_allowed_ips=allowed_ips,
                persistent_keepalive=keepalive,
                dns=server_config['dns'],
            )

            wireguard_config.save()

        api_client.update_server_config(interface, added_clients)

        messages.success(request, f'Added {client_count} clients to {server_config["name"]} interface')
        return redirect("index_wg_users")

    context = {
        'interfaces': interfaces,
        'allowed_ips_groups': allowed_ips_groups,
    }
    return render(request, "wg_users/create.html", context)


def download(request, wg_user_uuid):
    wireguard_config = WireguardConfig.objects.get(wg_user_uuid=wg_user_uuid)
    context = {
        'config': wireguard_config,
    }
    content = render_to_string('wg_users/wireguard-config.conf', context)
    response = HttpResponse(content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{wireguard_config.name}.conf"'
    return response


def update(request, wg_user_uuid):
    api_client = ApiClient(**request.user.default_api_client.to_dict())
    wg_user = api_client.get_client(wg_user_uuid)
    wg_user['uuid'] = wg_user_uuid
    interfaces = api_client.get_interfaces()
    allowed_ips_groups = request.user.allowedipsgroup_set.all().values('id', 'group_name')

    if request.method == "POST":
        wg_user.update(request.POST.dict())
        del wg_user['uuid'], wg_user['csrfmiddlewaretoken']
        api_client.set_client(wg_user_uuid, wg_user)

        wireguard_config = WireguardConfig.objects.get(wg_user_uuid=wg_user_uuid)
        if wireguard_config:
            wireguard_config.name = wg_user['name']
            wireguard_config.keepalive = wg_user['keepalive']
            wireguard_config.save()
        messages.success(request, f'Updated client {wg_user["name"]}')
        return redirect("index_wg_users")
    context = {
        'wg_user': wg_user,
        'interfaces': interfaces,
        'allowed_ips_groups': allowed_ips_groups,
    }
    return render(request, "wg_users/update.html", context)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete(request, wg_user_uuid):
    api_client = ApiClient(**request.user.default_api_client.to_dict())
    api_client.delete_client(wg_user_uuid)
    wireguard_config = WireguardConfig.objects.get(wg_user_uuid=wg_user_uuid)
    wg_user_name = None
    if wireguard_config:
        wg_user_name = wireguard_config.name
        wireguard_config.delete()
    messages.success(request, f'Deleted client {wg_user_name}')
    return JsonResponse({"status": "ok"})


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
@require_http_methods(["POST"])
def calculate_allowed_ips(request):
    allowed_ips_calculated = None
    if request.method == 'POST':
        data = json.loads(request.body)
        allowed_ips = data.get('allowed_ips')
        disallowed_ips = data.get('disallowed_ips')
        allowed_ips_calculated = wg_allowed_ips.calculate_allowed_ips(allowed_ips, disallowed_ips)

    return JsonResponse({'allowed_ips_calculated': allowed_ips_calculated})
