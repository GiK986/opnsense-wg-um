from django.views import generic as views
from django.contrib.auth import mixins as auth_mixins
from apps.utils.mixins import APIClientRequiredMixin


class DashboardView(auth_mixins.LoginRequiredMixin, APIClientRequiredMixin, views.TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_key = context.get('filter_key', None)
        clients = self.api_client.get_client_stats_by_filter(filter_key)
        status_count = self.api_client.get_client_stats_count()
        status_percent = self.api_client.get_client_stats_percent()

        context["status_count"] = status_count
        context["status_percent"] = status_percent
        context["clients"] = clients
        context["segment"] = "dashboard"
        return context
