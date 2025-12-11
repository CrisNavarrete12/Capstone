import pytest
from datetime import date, time
from happyhuapi.models import Booking
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_reserva_hora_inicio_menor_que_fin():
    booking = Booking(
        customer_name="Prueba",
        customer_email="test@test.com",
        customer_phone="+56900000000",
        event_date=date.today(),
        start_time=time(10, 0),
        end_time=time(9, 0),  # fin antes que inicio
        location="Local"
    )

    with pytest.raises(ValidationError):
        booking.full_clean()