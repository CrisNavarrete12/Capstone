import pytest
from django.urls import reverse
from datetime import date, time
from happyhuapi.models import Booking
from catalog.models import Product
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_reserva_fecha_pasada_invalida():
    ayer = date.today().replace(day=date.today().day - 1)

    b = Booking(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=ayer,
        start_time=time(10,0),
        end_time=time(11,0),
        location="Casa"
    )

    with pytest.raises(ValidationError):
        b.full_clean()

@pytest.mark.django_db
def test_reserva_horario_invalido_distinto_dia():
    b = Booking(
        customer_name="Test",
        customer_email="t@t.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(15,0),
        end_time=time(10,0),
        location="Local"
    )
    with pytest.raises(ValidationError):
        b.full_clean()

@pytest.mark.django_db
def test_reservas_solapadas_falla():
    Booking.objects.create(
        customer_name="A",
        customer_email="a@a.com",
        customer_phone="1",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )

    b2 = Booking(
        customer_name="B",
        customer_email="b@b.com",
        customer_phone="2",
        event_date=date.today(),
        start_time=time(10,30),
        end_time=time(11,30),
        location="Local"
    )

    with pytest.raises(ValidationError):
        b2.full_clean()

@pytest.mark.django_db
def test_reservas_json_ordenadas(client):
    admin = User.objects.create_user("admin","a@a.com","1234", is_staff=True)
    client.login(username="admin", password="1234")

    Booking.objects.create(
        customer_name="B",
        customer_email="b@b.com",
        customer_phone="1",
        event_date=date.today(),
        start_time=time(12,0),
        end_time=time(13,0),
        location="Local"
    )

    Booking.objects.create(
        customer_name="A",
        customer_email="a@a.com",
        customer_phone="1",
        event_date=date.today(),
        start_time=time(9,0),
        end_time=time(10,0),
        location="Local"
    )

    data = client.get(reverse("catalog:reservas_json")).json()

    assert data[0]["start"] < data[1]["start"]




