import qrcode
import os
import uuid
from django.conf import settings
from django.urls import reverse

def generar_qr_para_reserva(booking):

    # URL del QR (link al módulo de evidencia)
    url = settings.BASE_URL + reverse("evidencia_qr", args=[booking.id])

    # Generar imagen QR
    qr = qrcode.make(url)

    # Nombre único del archivo
    filename = f"qr_booking_{booking.id}_{uuid.uuid4().hex}.png"

    # Carpeta DESTINO real dentro de MEDIA_ROOT
    qr_dir = os.path.join(settings.MEDIA_ROOT, "qr_codes")
    os.makedirs(qr_dir, exist_ok=True)

    # Ruta física real donde se guardará
    full_path = os.path.join(qr_dir, filename)

    # Guardar la imagen en disco
    qr.save(full_path)

    # Asignar al campo ImageField correctamente (ruta relativa a MEDIA_ROOT)
    booking.qr_image.name = f"qr_codes/{filename}"
    booking.save(update_fields=["qr_image"])

    # Retornamos la ruta relativa para usarla si se necesita
    return booking.qr_image.name
