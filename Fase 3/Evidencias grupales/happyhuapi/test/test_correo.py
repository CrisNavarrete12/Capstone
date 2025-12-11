import pytest
from datetime import date, time
from django.core import mail
from happyhuapi.models import Booking
from happyhuapi.utils import enviar_correo_aprobacion

@pytest.mark.django_db
def test_envio_correo_aprobacion():
    booking = Booking.objects.create(
        customer_name="Juan Pérez",
        customer_email="juan@example.com",
        customer_phone="+56911111111",
        event_date=date(2025, 12, 1),
        start_time=time(10, 0),
        end_time=time(11, 0),
        location="Local"
    )

    # Llamar función correcta
    enviar_correo_aprobacion(booking)

    # Se debe haber enviado exactamente 1 correo
    assert len(mail.outbox) == 1

    correo = mail.outbox[0]
    assert correo.subject == "¡Tu reserva fue aprobada!"
    assert "Juan Pérez" in correo.body
    assert correo.to == ["juan@example.com"]