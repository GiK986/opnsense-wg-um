from io import BytesIO

import qrcode
from django.http import HttpResponse
from django.template.loader import render_to_string

from apps.wg_users.models import WireguardConfig


def get_wireguard_config(wg_user_uuid):
    wireguard_config = WireguardConfig.objects.filter(wg_user_uuid=wg_user_uuid).first()
    if not wireguard_config:
        raise ValueError("Wireguard config not found")

    context = {
        "config": wireguard_config,
    }
    content = render_to_string("wg_users/wireguard-config.conf", context)

    return wireguard_config.name, content


def generate_qrcode(wg_user_uuid):
    name, content = get_wireguard_config(wg_user_uuid)
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Add QR code image to HTTP response
    response = HttpResponse(content_type="image/png")
    img_io = BytesIO()
    img.save(img_io, "PNG")
    response.write(img_io.getvalue())

    return response
