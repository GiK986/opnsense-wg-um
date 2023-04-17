import uuid
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class WireguardConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wg_user_uuid = models.UUIDField(editable=True, unique=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    private_key = models.CharField(max_length=1000)
    public_key = models.CharField(max_length=1000)
    server_public_key = models.CharField(max_length=1000)
    server_endpoint = models.CharField(max_length=100)
    server_endpoint_port = models.IntegerField()
    server_allowed_ips = models.CharField(max_length=1000)
    persistent_keepalive = models.IntegerField()
    dns = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AllowedIpsGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length=100)
    allowed_ips = models.CharField(max_length=150)
    disallowed_ips = models.CharField(max_length=150)
    allowed_ips_calculated = models.CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.group_name
