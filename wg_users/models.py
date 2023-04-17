from django.db import models


# Create your models here.
class WireguardConfig(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True)
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
