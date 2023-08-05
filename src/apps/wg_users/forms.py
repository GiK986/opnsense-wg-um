from apps.utils.forms import BaseForm
from django.forms import Textarea
from django import forms
from .models import AllowedIpsGroup


class AllowedIpsGroupForm(BaseForm):
    class Meta:
        model = AllowedIpsGroup
        fields = "__all__"
        exclude = ['created_at', 'updated_at', 'user']
        widgets = {
            'allowed_ips_calculated': Textarea(attrs={'style': 'height: 160px'}),
        }


class WGUserUpdateForm(forms.Form):
    enabled = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'})
    )
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'})
    )
    keepalive = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Keep Alive'})
    )
