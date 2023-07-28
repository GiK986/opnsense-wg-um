from django.shortcuts import redirect
from django.contrib import messages
from apps.utils.api_client import ApiClient


class APIClientRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'default_api_client') and request.user.default_api_client is not None:
            return super().dispatch(request, *args, **kwargs)
        else:
            message = "You need to create an API client first."
            messages.warning(request, message)
            return redirect('create_api_client')

    @property
    def api_client(self):
        return ApiClient(**self.request.user.default_api_client.to_dict())
