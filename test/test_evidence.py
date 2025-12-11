import pytest
from datetime import date, time
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from happyhuapi.models import EvidencePhoto
from django.test import override_settings

from happyhuapi.models import Booking, Evidence


# Helper: crear usuario trabajador REAL según la función es_trabajador()
def crear_trabajador():
    g, _ = Group.objects.get_or_create(name="Trabajador")
    u = User.objects.create_user("trab", "t@t.com", "1234")
    u.groups.add(g)
    return u

@pytest.mark.django_db
def test_evidencia_qr_view_carga(client):
    user = crear_trabajador()
    client.login(username="trab", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10, 0),
        end_time=time(11, 0),
        location="Local"
    )

    url = reverse("evidencia_qr", args=[b.id])
    response = client.get(url)

    assert response.status_code == 200
    assert "Evidencia" in response.content.decode()


@pytest.mark.django_db
def test_registrar_llegada(client):
    user = crear_trabajador()
    client.login(username="trab", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Local"
    )

    url = reverse("registrar_llegada", args=[b.id])
    client.post(url)

    e = Evidence.objects.get(booking=b)
    assert e.arrival_time is not None


@pytest.mark.django_db
def test_registrar_salida(client):
    user = crear_trabajador()
    client.login(username="trab", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Local"
    )

    # Llegada primero (crea Evidence si no existe)
    client.post(reverse("registrar_llegada", args=[b.id]))

    # Ahora salida
    client.post(reverse("registrar_salida", args=[b.id]))

    e = Evidence.objects.get(booking=b)
    assert e.finish_time is not None


@pytest.mark.django_db
def test_actualizar_checklist(client):
    user = crear_trabajador()
    client.login(username="trab", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Local"
    )

    evidencia = Evidence.objects.get(booking=b)

    url = reverse("actualizar_checklist", args=[b.id])
    client.post(url, {"campo": "table_installed", "valor": "true"})

    evidencia.refresh_from_db()
    assert evidencia.table_installed is True


@pytest.mark.django_db
def test_finalizar_evidencia(client):
    user = crear_trabajador()
    client.login(username="trab", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Local"
    )

    evidencia = Evidence.objects.get(booking=b)

    url = reverse("finalizar_evidencia", args=[b.id])
    client.post(url)

    evidencia.refresh_from_db()
    assert evidencia.completed is True


@pytest.mark.django_db
def test_evidencia_admin_permiso(client):
    normal = User.objects.create_user("n", "n@n.com", "1234")
    client.login(username="n", password="1234")

    # Vista admin requiere booking_id
    url = reverse("evidencia_admin", args=[1])

    response = client.get(url)
    assert response.status_code in (302, 403)


@pytest.mark.django_db
def test_evidencia_pdf(client):
    admin = User.objects.create_user("admin", "a@a.com", "1234", is_staff=True)
    client.login(username="admin", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(9, 0),
        end_time=time(10, 0),
        location="Local"
    )

    url = reverse("evidencia_pdf", args=[b.id])
    response = client.get(url)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"


@pytest.mark.django_db
def test_evidencia_autocreada_por_signal():
    b = Booking.objects.create(
        customer_name="Test",
        customer_email="t@t.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(8, 0),
        end_time=time(9, 0),
        location="Casa"
    )

    assert Evidence.objects.filter(booking=b).exists()

@pytest.mark.django_db
def test_no_trabajador_no_puede_registrar_llegada(client):
    # Usuario normal sin grupo Trabajador
    user = User.objects.create_user("user", "x@x.com", "1234")
    client.login(username="user", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(12, 0),
        end_time=time(13, 0),
        location="Local"
    )

    url = reverse("registrar_llegada", args=[b.id])
    response = client.post(url)

    # Respuesta debe ser prohibido
    assert response.status_code == 403

    e = Evidence.objects.get(booking=b)
    assert e.arrival_time is None

@pytest.mark.django_db
def test_guardar_notas_evidencia(client):
    # Crear trabajador real
    g, _ = Group.objects.get_or_create(name="Trabajador")
    user = User.objects.create_user("trab", "t@t.com", "1234")
    user.groups.add(g)
    client.login(username="trab", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(14, 0),
        end_time=time(15, 0),
        location="Casa"
    )

    evidencia = Evidence.objects.get(booking=b)

    url = reverse("guardar_notas", args=[b.id])
    response = client.post(url, {"notas": "Todo instalado correctamente"})

    assert response.status_code == 200

    evidencia.refresh_from_db()
    assert evidencia.notes == "Todo instalado correctamente"

@pytest.mark.django_db
def test_subir_foto_sin_archivo(client):
    g,_ = Group.objects.get_or_create(name="Trabajador")
    t = User.objects.create_user("trab","t@t.com","1234")
    t.groups.add(g)
    client.login(username="trab", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )

    client.post(reverse("registrar_llegada", args=[b.id]))  # crea evidencia
    resp = client.post(reverse("subir_foto_evidencia", args=[b.id]), {})

    assert resp.status_code == 400

@pytest.mark.django_db
def test_checklist_campo_invalido(client):
    g,_ = Group.objects.get_or_create(name="Trabajador")
    t = User.objects.create_user("trab","t@t.com","1234")
    t.groups.add(g)
    client.login(username="trab", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )

    Evidence.objects.get(booking=b)

    url = reverse("actualizar_checklist", args=[b.id])
    resp = client.post(url, {"campo": "no_existe", "valor": "true"})

    assert resp.status_code == 400

@pytest.mark.django_db
def test_pdf_sin_fotos(client):
    admin = User.objects.create_user("admin","a@a.com","1234", is_staff=True)
    client.login(username="admin", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(7,0),
        end_time=time(8,0),
        location="Local"
    )

    Evidence.objects.get(booking=b)
    resp = client.get(reverse("evidencia_pdf", args=[b.id]))

    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/pdf"

@pytest.mark.django_db
def test_finalizar_evidencia_dos_veces(client):
    g,_ = Group.objects.get_or_create(name="Trabajador")
    t = User.objects.create_user("trab","t@t.com","1234")
    t.groups.add(g)
    client.login(username="trab", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )
    Evidence.objects.get(booking=b)

    url = reverse("finalizar_evidencia", args=[b.id])

    r1 = client.post(url)
    r2 = client.post(url)

    assert r1.status_code == 200
    assert r2.status_code == 200

@pytest.mark.django_db
def test_qr_reserva_inexistente(client):
    u = User.objects.create_user("trab","t@t.com","1234")
    client.login(username="trab", password="1234")

    url = reverse("evidencia_qr", args=[99999])
    resp = client.get(url)

    assert resp.status_code == 404

@override_settings(
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT="test_media/"
)
@pytest.mark.django_db
def test_qr_muestra_lista_fotos(client):
    g,_ = Group.objects.get_or_create(name="Trabajador")
    t = User.objects.create_user("trab","t@t.com","1234")
    t.groups.add(g)
    client.login(username="trab", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(9,0),
        end_time=time(10,0),
        location="Local"
    )

    evidencia = Evidence.objects.get(booking=b)
    EvidencePhoto.objects.create(evidence=evidencia, image=SimpleUploadedFile("a.jpg", b"xx"))
    EvidencePhoto.objects.create(evidence=evidencia, image=SimpleUploadedFile("b.jpg", b"xx"))

    resp = client.get(reverse("evidencia_qr", args=[b.id]))

    assert resp.status_code == 200
    assert "a.jpg" in resp.content.decode()
    assert "b.jpg" in resp.content.decode()

@pytest.mark.django_db
def test_admin_no_puede_registrar_llegada(client):
    admin = User.objects.create_user("admin","a@a.com","1234", is_staff=True)
    client.login(username="admin", password="1234")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )

    resp = client.post(reverse("registrar_llegada", args=[b.id]))
    assert resp.status_code == 403

@pytest.mark.django_db
def test_qr_requiere_login(client):
    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="a@a.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(8,0),
        end_time=time(9,0),
        location="Local"
    )

    resp = client.get(reverse("evidencia_qr", args=[b.id]))
    assert resp.status_code == 302   # redirect to login
