import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from catalog.models import Product
from django.contrib.auth.models import User

@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
@pytest.mark.django_db
def crear_producto():
    return Product.objects.create(
        name="Producto Test",
        description="Desc",
        price=1000,
        image=SimpleUploadedFile("x.jpg", b"x", content_type="image/jpeg"),
    )

@pytest.mark.django_db
@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
def test_carrito_inicia_vacio(client):
    assert client.session.get("carrito", []) == []

@pytest.mark.django_db
@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
def test_agregar_dos_veces(client):
    p = crear_producto()
    url = reverse("catalog:agregar_carrito", args=[p.id])
    client.get(url)
    client.get(url)
    assert client.session["carrito"] == [p.id, p.id]

@pytest.mark.django_db
def test_ver_carrito_view(client):
    User.objects.create_user(username="admin", password="admin123")
    client.login(username="admin", password="admin123")
    p = crear_producto()
    client.get(reverse("catalog:agregar_carrito", args=[p.id]))
    response = client.get(reverse("catalog:carrito"))
    assert response.status_code == 200
    assert "Planta" in response.content.decode() or "Producto Test" in response.content.decode()

@pytest.mark.django_db
def test_total_carrito(client):
    User.objects.create_user(username="admin", password="admin123")
    client.login(username="admin", password="admin123")
    p = crear_producto()
    client.get(reverse("catalog:agregar_carrito", args=[p.id]))
    response = client.get(reverse("catalog:carrito"))
    assert "1000" in response.content.decode()

@pytest.mark.django_db
def test_carrito_persiste_entre_requests(client):
    p = crear_producto()
    client.get(reverse("catalog:agregar_carrito", args=[p.id]))
    session_before = client.session["carrito"]
    client.get(reverse("catalog:lista"))
    assert client.session["carrito"] == session_before

@pytest.mark.django_db
def test_vaciar_carrito(client):
    p1 = Product.objects.create(name="A", description="d", price=1000)
    p2 = Product.objects.create(name="B", description="d", price=2000)

    client.get(f"/catalogo/agregar/{p1.id}/")
    client.get(f"/catalogo/agregar/{p2.id}/")

    client.get("/catalogo/vaciar/")

    carrito = client.session.get("carrito", [])
    assert carrito == []

@pytest.mark.django_db
def test_agregar_inexistente_carrito(client):
    response = client.get("/catalogo/agregar/9999/")
    assert response.status_code in (200, 302, 404)

@pytest.mark.django_db
def test_carrito_persiste_sesion(client):
    p = Product.objects.create(name="A", description="d", price=1000)

    client.get(f"/catalogo/agregar/{p.id}/")
    session1 = dict(client.session)

    client.get("/")
    session2 = dict(client.session)

    assert session1.get("carrito") == session2.get("carrito")


