import pytest
from django.urls import reverse
from datetime import date, time
from happyhuapi.models import Booking
from catalog.models import Product
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db
def test_calendario_json_retorna_lista(client):
    # Crear admin
    admin = User.objects.create_user("admin","a@a.com","1234", is_staff=True)
    client.login(username="admin", password="1234")

    # Crear reserva
    Booking.objects.create(
        customer_name="Cliente",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )

    response = client.get(reverse("catalog:reservas_json"))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

@pytest.mark.django_db
def test_reservas_json_tiene_campos(client):
    admin = User.objects.create_user("admin","x@x.com","1234", is_staff=True)
    client.login(username="admin", password="1234")

    reserva = Booking.objects.create(
        customer_name="Carlos",
        customer_email="c@c.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(9,0),
        end_time=time(10,0),
        location="Local"
    )

    response = client.get(reverse("catalog:reservas_json"))
    data = response.json()[0]

    assert "title" in data
    assert "start" in data
    assert "end" in data
    assert "extendedProps" in data

@pytest.mark.django_db
def test_editar_booking_admin_post(client):
    admin = User.objects.create_user("admin","x@a.com","1234", is_staff=True)
    client.login(username="admin", password="1234")

    r = Booking.objects.create(
        customer_name="Test",
        customer_email="e@e.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local",
        notes="vieja nota"
    )

    response = client.post(reverse("catalog:editar_booking_admin", args=[r.id]), {
        "customer_name": "Nuevo",
        "customer_email": "e@e.com",
        "customer_phone": "123",
        "event_date": date.today(),
        "start_time": "10:00",
        "end_time": "11:00",
        "location": "Local",
        "notes": "nueva nota"
    })

    r.refresh_from_db()
    assert r.customer_name == "Nuevo"
    assert r.notes == "nueva nota"

@pytest.mark.django_db
def test_editar_booking_admin_necesita_staff(client):
    user = User.objects.create_user("user","a@b.com","1234")
    client.login(username="user", password="1234")

    r = Booking.objects.create(
        customer_name="X",
        customer_email="x@x.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(9,0),
        end_time=time(10,0),
        location="Local"
    )

    response = client.post(reverse("catalog:editar_booking_admin", args=[r.id]), {})
    assert response.status_code == 302

@pytest.mark.django_db
def test_editar_booking_inexistente_404(client):
    admin = User.objects.create_user("admin","x@x.com","1234", is_staff=True)
    client.login(username="admin", password="1234")

    response = client.get(reverse("catalog:editar_booking_admin", args=[9999]))
    assert response.status_code == 404

@pytest.mark.django_db
def test_carrito_calcula_deposito_correcto(client):
    user = User.objects.create_user("admin","admin@x.com","1234")
    client.login(username="admin", password="1234")

    p = Product.objects.create(name="Producto", description="x", price=1000)

    client.get(reverse("catalog:agregar_carrito", args=[p.id]))

    response = client.get(reverse("catalog:carrito"))
    contenido = response.content.decode()

    assert "300" in contenido  # 30% de 1000

@pytest.mark.django_db
def test_lista_productos_ordenados(client):
    p1 = Product.objects.create(name="B", description="x", price=100)
    p2 = Product.objects.create(name="A", description="x", price=100)

    response = client.get(reverse("catalog:lista"))
    productos = list(response.context["productos"])

    assert productos[0].id < productos[1].id

@pytest.mark.django_db
def test_crear_productos_duplicados_no_rompe():
    Product.objects.create(name="X", description="x", price=100)
    Product.objects.create(name="X", description="x", price=100)
    assert Product.objects.filter(name="X").count() == 2

@pytest.mark.django_db
def test_template_crear_producto(client):
    admin = User.objects.create_user("admin","x@x.com","1234", is_staff=True)
    client.login(username="admin", password="1234")

    response = client.get(reverse("catalog:agregar"))
    assert "catalog/formulario_producto.html" in [t.name for t in response.templates]

def test_url_editar_booking_admin_existe():
    try:
        url = reverse("catalog:editar_booking_admin", args=[1])
        print("URL:", url)
        assert True
    except Exception as e:
        print("ERROR:", e)
        assert False





