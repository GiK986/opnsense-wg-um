from django.forms import ModelForm
from django.forms.widgets import Textarea


class BaseForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        for field_name, field in self.fields.items():
            if isinstance(field.widget, Textarea):
                field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})
            else:
                if field.widget.input_type == 'text':
                    field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})
                elif field.widget.input_type == 'password':
                    field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})
                elif field.widget.input_type == 'checkbox':
                    field.widget.attrs.update({'class': 'form-check-input'})
                elif field.widget.input_type == 'select':
                    field.widget.attrs.update({'class': 'form-select'})
                elif isinstance(field.widget, Textarea):
                    field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance
