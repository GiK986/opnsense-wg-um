from io import BytesIO

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from apps.utils.pywgtools.wgtools import pubkey
from apps.wg_users.models import WireguardConfig
from apps.wg_users.views import generate_qrcode
from core import settings


def send_email(wg_user_uuid, email_sender):
    wireguard_config = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()
    if not wireguard_config:
        return {"status": "error", "message": "Wireguard config not found"}

    context = {
        "config": wireguard_config,
    }
    content = render_to_string("wg_users/wireguard-config.conf", context)
    file_buffer = BytesIO(content.encode("utf-8"))

    subject = f"Wireguard config for {wireguard_config.name}"
    message = f"Wireguard config for {wireguard_config.name}"
    email_from = settings.DEFAULT_FROM_EMAIL
    email_message = EmailMessage(subject, message, email_from, [email_sender])
    email_message.attach(f"{wireguard_config.name}.conf", file_buffer.getvalue(), "application/octet-stream")

    wg_user_qrcode = generate_qrcode(wg_user_uuid)
    email_message.attach(f"{wireguard_config.name}.png", wg_user_qrcode.getvalue(), "image/png")

    email_message.send()

    return {"status": "ok"}


def parse_wireguard_config(file_content):
    config = {}

    for line in file_content.splitlines():

        if '=' in line.strip():
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            config[key] = value

    errors = validate_wireguard_config(config)

    if errors:
        raise ValueError(errors)

    config["public_key"] = get_pubkey_by_private_key(config["PrivateKey"])
    return config


def validate_wireguard_config(config):
    errors = []

    if "Address" not in config:
        errors.append("Address not found")

    if "PrivateKey" not in config:
        errors.append("PrivateKey not found")

    if "Endpoint" not in config:
        errors.append("Endpoint not found")

    if "PublicKey" not in config:
        errors.append("PublicKey not found")

    return errors


def get_pubkey_by_private_key(private_key):
    return pubkey(private_key)


def create_or_update_wireguard_config(config):
    wireguard_config = WireguardConfig.objects.filter(wg_user_uuid=config["wg_user_uuid"]).first()
    if wireguard_config:
        wireguard_config.name = config["name"]
        wireguard_config.address = config["address"]
        wireguard_config.private_key = config["private_key"]
        wireguard_config.public_key = config["public_key"]
        wireguard_config.server_public_key = config["server_public_key"]
        wireguard_config.server_endpoint = config["server_endpoint"]
        wireguard_config.server_endpoint_port = config["server_endpoint_port"]
        wireguard_config.server_allowed_ips = config["server_allowed_ips"]
        wireguard_config.persistent_keepalive = config["persistent_keepalive"]
        wireguard_config.dns = config["dns"]
    else:
        wireguard_config = WireguardConfig.objects.create(
            wg_user_uuid=config["wg_user_uuid"],
            name=config["name"],
            address=config["address"],
            private_key=config["private_key"],
            public_key=config["public_key"],
            server_public_key=config["server_public_key"],
            server_endpoint=config["server_endpoint"],
            server_endpoint_port=config["server_endpoint_port"],
            server_allowed_ips=config["server_allowed_ips"],
            persistent_keepalive=config["persistent_keepalive"],
            dns=config["dns"],
        )

    wireguard_config.save()
