from utils.forms import BaseForm
from django.forms import Textarea
from .models import AllowedIpsGroup


class AllowedIpsGroupForm(BaseForm):
    class Meta:
        model = AllowedIpsGroup
        fields = "__all__"
        exclude = ['created_at', 'updated_at', 'user']
        widgets = {
            'allowed_ips_calculated': Textarea(attrs={'style': 'height: 160px'}),
        }
