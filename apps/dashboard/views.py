from django.views import generic as views
from django.contrib.auth import mixins as auth_mixins
from apps.utils.mixins import APIClientRequiredMixin
from apps.wg_users.models import WireguardConfig


class DashboardView(auth_mixins.LoginRequiredMixin, APIClientRequiredMixin, views.TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_key = context.get('filter_key', None)
        clients = self.api_client.get_client_stats_by_filter(filter_key)
        status_count = self.api_client.get_client_stats_count()
        status_percent = self.api_client.get_client_stats_percent()

        wg_user_configs = WireguardConfig.objects.all().values('wg_user_uuid')

        for client in clients:
            for wg_user_config in wg_user_configs:
                client['config'] = False
                if client['uuid'] == str(wg_user_config['wg_user_uuid']):
                    client['config'] = True
                    break

        context.update({
            "segment": "dashboard",
            "clients": clients,
            "status_count": status_count,
            "status_percent": status_percent,
        })

        return context
