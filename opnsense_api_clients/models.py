import uuid

from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class OpnSenseApiClient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    friendly_name = models.CharField(max_length=60)
    endpoint_url = models.CharField(max_length=150)
    base_url = models.CharField(max_length=150)
    api_key = models.CharField(max_length=150)
    api_secret = models.CharField(max_length=150)
    is_default = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.friendly_name
