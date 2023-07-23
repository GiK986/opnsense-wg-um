import json
import qrcode
from io import BytesIO
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.views import generic as views
from django.contrib.auth import mixins as auth_mixins
from django.urls import reverse_lazy

from core import settings
from apps.utils.api_client import ApiClient
from apps.utils.pywgtools import wg_allowed_ips
from apps.utils.pywgtools.wgtools import genkey, pubkey
from .forms import AllowedIpsGroupForm
from .models import WireguardConfig, AllowedIpsGroup
from django.contrib import messages
from apps.utils.decorators import api_client_required
from apps.utils import mixins as utils_mixins


class WGUsersIndexView(auth_mixins.LoginRequiredMixin, utils_mixins.APIClientRequiredMixin, views.TemplateView):
    template_name = "wg_users/index.html"
    segment = "index_wg_users"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        interface_clients = self.api_client.get_interface_clients()
        wg_user_configs = WireguardConfig.objects.all().values("wg_user_uuid")

        for client in interface_clients:
            for wg_user_config in wg_user_configs:
                client["config"] = False
                if client["uuid"] == str(wg_user_config["wg_user_uuid"]):
                    client["config"] = True
                    break

        context.update({
            "wg_users": interface_clients,
            "segment": "index_wg_users",
            "page": {
                "title": "WireGuard Users",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                ]
            }
        })

        return context


class WGUsersCreateView(auth_mixins.LoginRequiredMixin, utils_mixins.APIClientRequiredMixin, views.CreateView):
    template_name = 'wg_users/create.html'
    model = WireguardConfig
    fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        interfaces = self.api_client.get_interfaces()
        allowed_ips_groups = self.request.user.allowedipsgroup_set.all().values("id", "group_name")

        context.update({
            "interfaces": interfaces,
            "allowed_ips_groups": allowed_ips_groups,
            "segment": "index_wg_users",
            "page": {
                "title": "Create WireGuard Users",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"name": "WireGuard Users", "url": reverse_lazy("index_wg_users")},
                ]
            }
        })

        return context

    def form_valid(self, form):
        interface = form.data.get("interface")
        allowed_ips_group = form.data.get("allowed_ips_group")
        prefix_users = form.data.get("prefix_users")
        keepalive = int(form.data.get("keepalive"))
        client_count = int(form.data.get("client_count"))
        server_endpoint = self.request.user.default_api_client.endpoint_url
        allowed_ips = self.request.user.allowedipsgroup_set.get(id=allowed_ips_group).allowed_ips_calculated

        server_config = self.api_client.get_server_config(interface)
        hosts_iterator = self.api_client.get_hosts_iterator(interface)

        added_clients = []
        for _ in range(client_count):
            private_key = genkey()
            public_key = pubkey(private_key)
            available_host = str(next(hosts_iterator))
            name = f'{prefix_users}_{available_host.split(".")[-1]}'

            wg_user_uuid = self.api_client.add_client(name, public_key, available_host)
            added_clients.append(wg_user_uuid)

            wireguard_config = WireguardConfig(
                wg_user_uuid=wg_user_uuid,
                name=name,
                address=available_host,
                private_key=private_key,
                public_key=public_key,
                server_public_key=server_config["pubkey"],
                server_endpoint=server_endpoint,
                server_endpoint_port=server_config["port"],
                server_allowed_ips=allowed_ips,
                persistent_keepalive=keepalive,
                dns=server_config["dns"],
            )

            wireguard_config.save()

        self.api_client.update_server_config(interface, added_clients)

        messages.success(self.request, f'Added {client_count} clients to {server_config["name"]} interface')
        return redirect("index_wg_users")

    def form_invalid(self, form):
        return render(self.request, self.template_name, {"form": form})

    def get_success_url(self):
        return reverse_lazy("index_wg_users")


class WGUsersUpdateView(auth_mixins.LoginRequiredMixin, utils_mixins.APIClientRequiredMixin, views.UpdateView):
    template_name = 'wg_users/update.html'
    model = WireguardConfig
    fields = []
    pk_url_kwarg = "wg_user_uuid"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        interfaces = self.api_client.get_interfaces()
        allowed_ips_groups = self.request.user.allowedipsgroup_set.all().values("id", "group_name")

        context.update({
            "interfaces": interfaces,
            "allowed_ips_groups": allowed_ips_groups,
            "segment": "index_wg_users",
            "page": {
                "title": "Update WireGuard User",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"name": "WireGuard Users", "url": reverse_lazy("index_wg_users")},
                ]
            }
        })

        return context



@api_client_required
@login_required
def update(request, wg_user_uuid):
    api_client = ApiClient(**request.user.default_api_client.to_dict())
    wg_user = api_client.get_client(wg_user_uuid)
    wg_user["uuid"] = wg_user_uuid
    interfaces = api_client.get_interfaces()
    allowed_ips_groups = request.user.allowedipsgroup_set.all().values("id", "group_name")
    wireguard_config = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()
    wg_user["config"] = False
    if wireguard_config:
        wg_user["config"] = True

    if request.method == "POST":
        wg_user.update(request.POST.dict())
        del wg_user["uuid"], wg_user["csrfmiddlewaretoken"], wg_user["config"]
        api_client.set_client(wg_user_uuid, wg_user)

        if wireguard_config:
            wireguard_config.name = wg_user["name"]
            wireguard_config.keepalive = wg_user["keepalive"]
            wireguard_config.save()
        messages.success(request, f'Updated client {wg_user["name"]}')
        return redirect("index_wg_users")

    context = {
        "wg_user": wg_user,
        "interfaces": interfaces,
        "allowed_ips_groups": allowed_ips_groups,
        "page": {
            "title": "Update WireGuard User",
            "breadcrumbs": [
                {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                {"name": "WireGuard Users", "url": reverse_lazy("index_wg_users")},
            ]
        }
    }
    return render(request, "wg_users/update.html", context)


@csrf_exempt
@api_client_required
@login_required
@require_http_methods(["DELETE"])
def delete(request, wg_user_uuid):
    api_client = ApiClient(**request.user.default_api_client.to_dict())
    wg_user_name = api_client.get_client(wg_user_uuid)["name"]
    api_client.delete_client(wg_user_uuid)
    wireguard_config = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()

    if wireguard_config:
        wireguard_config.delete()

    messages.success(request, f"Deleted client {wg_user_name}")

    return JsonResponse({"status": "ok"})


@csrf_exempt
@api_client_required
@login_required
@require_http_methods(["POST"])
def reconfiguration(request, wg_user_uuid):
    data = json.loads(request.body)
    interface_uuid = data["interface_uuid"]
    allowed_ips_group_id = data["allowed_ips_group"]
    api_client = ApiClient(**request.user.default_api_client.to_dict())
    wg_user = api_client.get_client(wg_user_uuid)
    wg_user["keepalive"] = wg_user["keepalive"] if wg_user["keepalive"] else 15
    wireguard_config = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()

    server_config = api_client.get_server_config(interface_uuid)
    allowed_ips = request.user.allowedipsgroup_set.get(id=allowed_ips_group_id).allowed_ips_calculated
    server_endpoint = request.user.default_api_client.endpoint_url
    private_key = genkey()
    public_key = pubkey(private_key)

    if not wireguard_config:
        wireguard_config = WireguardConfig(
            wg_user_uuid=wg_user_uuid,
            name=wg_user["name"],
            address=wg_user["tunneladdress"],
            private_key=private_key,
            public_key=public_key,
            server_public_key=server_config["pubkey"],
            server_endpoint=server_endpoint,
            server_endpoint_port=server_config["port"],
            server_allowed_ips=allowed_ips,
            persistent_keepalive=wg_user["keepalive"],
            dns=server_config["dns"],
        )
        wireguard_config.save()
    else:
        wireguard_config.private_key = private_key
        wireguard_config.public_key = public_key
        wireguard_config.server_public_key = server_config["pubkey"]
        wireguard_config.server_endpoint = server_endpoint
        wireguard_config.server_endpoint_port = server_config["port"]
        wireguard_config.server_allowed_ips = allowed_ips
        wireguard_config.persistent_keepalive = wg_user["keepalive"]
        wireguard_config.dns = server_config["dns"]
        wireguard_config.save()

    wg_user["pubkey"] = public_key
    api_client.set_client(wg_user_uuid, wg_user)
    api_client.service_reconfigure()

    messages.success(request, f'Reconfigured client {wg_user["name"]}')
    return JsonResponse({"status": "ok"})


def download(request, wg_user_uuid):
    wireguard_config = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()
    if not wireguard_config:
        messages.error(request, "Wireguard config not found")
        return redirect(request.META.get("HTTP_REFERER"))

    context = {
        "config": wireguard_config,
    }
    content = render_to_string("wg_users/wireguard-config.conf", context)
    response = HttpResponse(content, content_type="application/octet-stream")
    response["Content-Disposition"] = f'attachment; filename="{wireguard_config.name}.conf"'
    return response


def generate_qrcode(request, wg_user_uuid):
    wireguard_config = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()
    if not wireguard_config:
        messages.error(request, "Wireguard config not found")
        return redirect(request.META.get("HTTP_REFERER"))

    context = {
        "config": wireguard_config,
    }
    content = render_to_string("wg_users/wireguard-config.conf", context)

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Add QR code image to HTTP response
    response = HttpResponse(content_type="image/png")
    img_io = BytesIO()
    img.save(img_io, "PNG")
    response.write(img_io.getvalue())

    return response


def download_qrcode(request, wg_user_uuid):
    response = generate_qrcode(request, wg_user_uuid)
    wg_user_name = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first().name
    response["Content-Disposition"] = f'attachment; filename="{wg_user_name}.png"'
    return response


def share_qrcode_link(request, wg_user_uuid):
    wg_user = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()
    wg_user_name = "Not found"
    wg_user_config = False
    if wg_user:
        wg_user_name = wg_user.name
        wg_user_config = True

    content = {
        "wg_user_uuid": wg_user_uuid,
        "wg_user_name": wg_user_name,
        "wg_user_config": wg_user_config,
    }

    return render(request, "wg_users/share_qrcode_link.html", content)


@csrf_exempt
@require_POST
def get_qrcode_link(request):
    data = json.loads(request.body)
    wg_user_uuid = data["wg_user_uuid"]

    return JsonResponse({"link": f"{request.scheme}://{request.get_host()}/wg_users/share_qrcode_link/{wg_user_uuid}/"})


@csrf_exempt
@login_required
def search(request, q):
    api_client = ApiClient(**request.user.default_api_client.to_dict())
    wg_users = api_client.get_clients(q)
    results = list(map(lambda k: {"title": k["name"],
                                  "url": f"{request.scheme}://{request.get_host()}/wg_users/update/{k['uuid']}/"
                                  },
                       wg_users))
    return JsonResponse(results, safe=False)


@csrf_exempt
@login_required
def send_email(request, wg_user_uuid):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data["email"]
        wireguard_config = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()
        if not wireguard_config:
            messages.error(request, "Wireguard config not found")
            return JsonResponse({"status": "error"})

        context = {
            "config": wireguard_config,
        }
        content = render_to_string("wg_users/wireguard-config.conf", context)
        file_buffer = BytesIO(content.encode("utf-8"))

        subject = f"Wireguard config for {wireguard_config.name}"
        message = f"Wireguard config for {wireguard_config.name}"
        email_from = settings.DEFAULT_FROM_EMAIL
        email_message = EmailMessage(subject, message, email_from, [email])
        email_message.attach(f"{wireguard_config.name}.conf", file_buffer.getvalue(), "application/octet-stream")

        wg_user_qrcode = generate_qrcode(request, wg_user_uuid)
        email_message.attach(f"{wireguard_config.name}.png", wg_user_qrcode.getvalue(), "image/png")

        email_message.send()

        messages.success(request, f"Email sent to {email}")
        return JsonResponse({"status": "ok"})


# AllowedIpsGroup
class AllowedIPsGroupIndexView(auth_mixins.LoginRequiredMixin, views.TemplateView):
    template_name = "allowed_ips_group/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "allowed_ips_groups": self.request.user.allowedipsgroup_set.all(),
            "segment": "index_allowed_ips_group",
            "page": {
                "title": "Allowed IPs Groups",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                ]
            }
        })

        return context


class AllowedIPsGroupCreateView(auth_mixins.LoginRequiredMixin, views.CreateView):
    template_name = "allowed_ips_group/create.html"
    form_class = AllowedIpsGroupForm
    success_url = reverse_lazy("index_allowed_ips_group")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "button_text": "Create",
            "segment": "index_allowed_ips_group",
            "page": {
                "title": "Create Allowed IPs Group",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"name": "Allowed IPs Groups", "url": reverse_lazy("index_allowed_ips_group")},
                ]
            }
        })

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "user": self.request.user,
        })
        return kwargs


class AllowedIPsGroupUpdateView(auth_mixins.LoginRequiredMixin, views.UpdateView):
    template_name = "allowed_ips_group/create.html"
    form_class = AllowedIpsGroupForm
    success_url = reverse_lazy("index_allowed_ips_group")
    model = AllowedIpsGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "button_text": "Update",
            "segment": "index_allowed_ips_group",
            "page": {
                "title": "Update Allowed IPs Group",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"name": "Allowed IPs Groups", "url": reverse_lazy("index_allowed_ips_group")},
                ]
            }
        })

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "user": self.request.user,
        })
        return kwargs


class AllowedIPsGroupDeleteView(auth_mixins.LoginRequiredMixin, views.DeleteView):
    template_name = "allowed_ips_group/delete.html"
    success_url = reverse_lazy("index_allowed_ips_group")
    model = AllowedIpsGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "segment": "index_allowed_ips_group",
            "page": {
                "title": "Delete Allowed IPs Group",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"name": "Allowed IPs Groups", "url": reverse_lazy("index_allowed_ips_group")},
                ]
            }
        })

        return context


@login_required
def allowed_ips_group_delete(request, allowed_ips_group_id):
    allowed_ips_group = request.user.allowedipsgroup_set.get(id=allowed_ips_group_id)
    if request.method == "POST":
        allowed_ips_group.delete()
        return redirect("index_allowed_ips_group")

    context = {"allowed_ips_group": allowed_ips_group}
    return render(request, "allowed_ips_group/delete.html", context)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def calculate_allowed_ips(request):
    allowed_ips_calculated = None
    if request.method == "POST":
        data = json.loads(request.body)
        allowed_ips = data.get("allowed_ips")
        disallowed_ips = data.get("disallowed_ips")
        allowed_ips_calculated = wg_allowed_ips.calculate_allowed_ips(allowed_ips, disallowed_ips)

    return JsonResponse({"allowed_ips_calculated": allowed_ips_calculated})
