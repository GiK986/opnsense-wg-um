import json
from django.http import JsonResponse
from django.shortcuts import redirect
from .forms import OpnSenseApiClientForm
from .models import OpnSenseApiClient
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from apps.utils.api_client import ApiClient
from django.views import generic as views
from django.contrib.auth import mixins as auth_mixins
from django.urls import reverse_lazy


class OpnSenseApiClientIndexView(auth_mixins.LoginRequiredMixin, views.TemplateView):
    template_name = "opnsense_api_clients/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "api_clients": self.request.user.opnsenseapiclient_set.all(),
            "segment": "index_api_clients",
            "page": {
                "title": "OpnSense API clients",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                ]
            }
        })
        return context


class OpnSenseApiClientCreateView(auth_mixins.LoginRequiredMixin, views.CreateView):
    template_name = "opnsense_api_clients/create.html"
    form_class = OpnSenseApiClientForm
    success_url = reverse_lazy("index_api_clients")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "segment": "index_api_clients",
            "page": {
                "title": "Create OpnSense API client",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"name": "OpnSense API clients", "url": reverse_lazy("index_api_clients")},
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


class OpnSenseApiClientUpdateView(auth_mixins.LoginRequiredMixin, views.UpdateView):
    template_name = "opnsense_api_clients/update.html"
    form_class = OpnSenseApiClientForm
    success_url = reverse_lazy("index_api_clients")
    model = OpnSenseApiClient

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "segment": "index_api_clients",
            "page": {
                "title": "Update OpnSense API client",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"name": "OpnSense API clients", "url": reverse_lazy("index_api_clients")},
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


class DeleteView(auth_mixins.LoginRequiredMixin, views.DeleteView):
    template_name = "opnsense_api_clients/delete.html"
    model = OpnSenseApiClient
    success_url = reverse_lazy("index_api_clients")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "segment": "index_api_clients",
            "page": {
                "title": "Delete OpnSense API client",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"name": "OpnSense API clients", "url": reverse_lazy("index_api_clients")},
                ]
            }
        })
        return context


@login_required
def set_default(request, pk):
    current_api_client = request.user.default_api_client
    set_default_api_client = OpnSenseApiClient.objects.get(id=pk)

    if current_api_client and current_api_client != set_default_api_client:
        current_api_client.is_default = False
        current_api_client.save()

        set_default_api_client.is_default = True
        set_default_api_client.save()

    return redirect(request.META['HTTP_REFERER'])


@login_required
@require_POST
@csrf_exempt
def test_connection(request):
    if request.method == "POST":
        data = json.loads(request.body)
        base_url = data.get('base_url')
        api_key = data.get('api_key')
        api_secret = data.get('api_secret')
        api_client = ApiClient(base_url=base_url, api_key=api_key, api_secret=api_secret)
        result = api_client.test_connection()
        if result[0]:
            return JsonResponse({'status': 'success', 'message': result[1]})

        return JsonResponse({'status': 'error', 'message': result[1]})
