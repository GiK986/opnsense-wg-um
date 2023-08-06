from io import BytesIO

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

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
