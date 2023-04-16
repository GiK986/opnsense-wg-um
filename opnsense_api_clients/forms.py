from django.forms import ModelForm, HiddenInput, ModelChoiceField
from .models import OpnSenseApiClient
from django.contrib.auth.models import User


class BaseForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        # self.fields['user'].initial = user
        # self.fields['user'].widget = HiddenInput()

        # Set the CSS classes for all text fields
        for field_name, field in self.fields.items():
            if field.widget.input_type == 'text':
                field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})
            elif field.widget.input_type == 'password':
                field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})
            elif field.widget.input_type == 'checkbox':
                field.widget.attrs.update({'class': 'form-check-input'})

    # user = ModelChoiceField(queryset=User.objects.all(), widget=HiddenInput())

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance


class OpnSenseApiClientForm(BaseForm):
    class Meta:
        model = OpnSenseApiClient
        fields = "__all__"
        exclude = ['created_at', 'updated_at', 'user']
