from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views import generic as views
from django.contrib.auth import mixins as auth_mixins
from django.urls import reverse_lazy

from apps.utils.pywgtools.wgtools import genkey, pubkey
from .forms import AllowedIpsGroupForm, WGUserUpdateForm
from .models import WireguardConfig, AllowedIpsGroup
from django.contrib import messages
from apps.utils import mixins as utils_mixins
from .services import get_wireguard_config, generate_qrcode


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


class WGUsersUpdateView(auth_mixins.LoginRequiredMixin, utils_mixins.APIClientRequiredMixin, views.FormView):
    template_name = 'wg_users/update.html'
    form_class = WGUserUpdateForm
    success_url = reverse_lazy("index_wg_users")

    def get_initial(self):
        initial = super().get_initial()
        initial.update(self.api_client.get_client(self.kwargs["wg_user_uuid"]))
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wg_user_uuid = self.kwargs["wg_user_uuid"]
        wg_user = self.api_client.get_client(wg_user_uuid)
        interfaces = self.api_client.get_interfaces()
        allowed_ips_groups = self.request.user.allowedipsgroup_set.all().values("id", "group_name")
        wireguard_config = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()
        wg_user_has_config = False
        if wireguard_config:
            wg_user_has_config = True

        context.update({
            "wg_user": wg_user,
            "interfaces": interfaces,
            "allowed_ips_groups": allowed_ips_groups,
            "wg_user_uuid": wg_user_uuid,
            "wg_user_has_config": wg_user_has_config,
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

    def form_valid(self, form):
        wg_user_uuid = self.kwargs.get("wg_user_uuid")
        wg_user = self.api_client.get_client(wg_user_uuid)

        before_update_enabled = wg_user["enabled"]
        wg_user.update(form.cleaned_data)
        after_update_enabled = wg_user["enabled"]
        self.api_client.set_client(wg_user_uuid, wg_user)

        if not before_update_enabled == after_update_enabled:
            self.api_client.client_set()
            self.api_client.service_reconfigure()

        wireguard_config = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()
        if wireguard_config:
            wireguard_config.name = wg_user["name"]
            wireguard_config.keepalive = wg_user["keepalive"]
            wireguard_config.save()

        messages.success(self.request, f'Updated client {wg_user["name"]}')
        return super().form_valid(form)


class ShareQrCodeLinkView(views.TemplateView):
    template_name = "wg_users/share_qrcode_link.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wg_user_uuid = kwargs["wg_user_uuid"]
        wg_user = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()
        wg_user_name = "Not found"
        wg_user_config = False
        if wg_user:
            wg_user_name = wg_user.name
            wg_user_config = True

        context.update(
            {
                "wg_user_uuid": wg_user_uuid,
                "wg_user_name": wg_user_name,
                "wg_user_config": wg_user_config,
            }
        )
        return context


class DownloadWireguardConfigFileView(views.View):

    @staticmethod
    def get(request, wg_user_uuid):
        try:
            name, content = get_wireguard_config(wg_user_uuid)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect(request.META.get("HTTP_REFERER"))

        response = HttpResponse(content, content_type="application/octet-stream")
        response["Content-Disposition"] = f'attachment; filename="{name}.conf"'
        return response


@login_required()
def get_generated_qrcode(request, wg_user_uuid):
    try:
        return generate_qrcode(wg_user_uuid)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect(request.META.get("HTTP_REFERER"))


# == AllowedIpsGroup == #
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
