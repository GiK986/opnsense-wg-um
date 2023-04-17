from django.contrib import admin
from .models import WireguardConfig, AllowedIpsGroup

# Register your models here.
admin.site.register(WireguardConfig)
admin.site.register(AllowedIpsGroup)
