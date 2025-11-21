import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from catalog.models import Product

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
    p = crear_producto()
    client.get(reverse("catalog:agregar_carrito", args=[p.id]))
    response = client.get(reverse("catalog:carrito"))
    assert response.status_code == 200
    assert "Planta" in response.content.decode() or "Producto Test" in response.content.decode()

@pytest.mark.django_db
def test_total_carrito(client):
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
