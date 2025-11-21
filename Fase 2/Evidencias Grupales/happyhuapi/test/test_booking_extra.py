import pytest
from datetime import date, time
from happyhuapi.models import Booking
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_reserva_valida():
    b = Booking(
        customer_name="Ana",
        customer_email="ana@example.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )
    b.full_clean()  # No debe lanzar error

@pytest.mark.django_db
def test_reserva_sin_email_falla():
    b = Booking(
        customer_name="Ana",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )
    with pytest.raises(Exception):
        b.full_clean()

@pytest.mark.django_db
def test_reserva_mismo_horario_igual_falla():
    b = Booking(
        customer_name="Ana",
        customer_email="ana@example.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(10,0),
        location="Local"
    )
    with pytest.raises(ValidationError):
        b.full_clean()

@pytest.mark.django_db
def test_reserva_minutos_no_permitidos():
    b = Booking(
        customer_name="Ana",
        customer_email="ana@example.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,30),
        end_time=time(11,0),
        location="Local"
    )
    with pytest.raises(ValidationError):
        b.full_clean()

@pytest.mark.django_db
def test_str_booking():
    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="ana@example.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )
    assert str(b) != ""
