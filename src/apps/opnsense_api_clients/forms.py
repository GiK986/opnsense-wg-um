from .models import OpnSenseApiClient
from apps.utils.forms import BaseForm


class OpnSenseApiClientForm(BaseForm):
    class Meta:
        model = OpnSenseApiClient
        fields = "__all__"
        exclude = ['created_at', 'updated_at', 'user']
