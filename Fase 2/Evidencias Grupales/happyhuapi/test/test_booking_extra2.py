import pytest
from datetime import date, time
from happyhuapi.models import Booking

@pytest.mark.django_db
def test_reserva_se_guarda_correctamente():
    b = Booking.objects.create(
        customer_name="Juan",
        customer_email="j@example.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(9,0),
        end_time=time(10,0),
        location="Local"
    )
    assert Booking.objects.count() == 1
    assert str(b) != ""

@pytest.mark.django_db
def test_filtrar_reservas_por_dia():
    hoy = date.today()
    Booking.objects.create(customer_name="A", customer_email="a@a.com", customer_phone="1", event_date=hoy, start_time=time(9,0), end_time=time(10,0), location="x")
    Booking.objects.create(customer_name="B", customer_email="b@b.com", customer_phone="1", event_date=hoy, start_time=time(11,0), end_time=time(12,0), location="x")
    assert Booking.objects.filter(event_date=hoy).count() == 2
