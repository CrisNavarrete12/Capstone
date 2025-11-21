import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from catalog.models import Product

@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
@pytest.mark.django_db
def test_lista_productos_view(client):
    response = client.get(reverse("catalog:lista"))
    assert response.status_code == 200

@pytest.mark.django_db
def test_detalle_producto_view(client):
    p = Product.objects.create(name="Test", description="x", price=100, image="x.jpg")
    response = client.get(reverse("catalog:detalle", args=[p.id]))
    assert response.status_code == 200

@pytest.mark.django_db
def test_crear_producto_admin_requiere_login(client):
    response = client.get(reverse("catalog:agregar"))
    assert response.status_code == 302  # redirige al login

@pytest.mark.django_db
def test_editar_producto_admin_requiere_login(client):
    p = Product.objects.create(name="Test", description="x", price=100, image="x.jpg")
    response = client.get(reverse("catalog:editar", args=[p.id]))
    assert response.status_code == 302

@pytest.mark.django_db
def test_eliminar_producto_admin_requiere_login(client):
    p = Product.objects.create(name="Test", description="x", price=100, image="x.jpg")
    response = client.get(reverse("catalog:eliminar", args=[p.id]))
    assert response.status_code == 302
