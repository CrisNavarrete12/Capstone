import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from catalog.models import Product
from django.contrib.auth.models import User

@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
@pytest.mark.django_db
def test_carrito_no_se_rompe_con_producto_inexistente(client):
    url = reverse("catalog:agregar_carrito", args=[999])  # ID inexistente
    response = client.get(url)
    assert response.status_code in (200, 302)  # No debe crashear

@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
@pytest.mark.django_db
def test_carrito_con_multiples_productos(client):
    def crear(nombre):
        return Product.objects.create(
            name=nombre,
            description="desc",
            price=1000,
            image=SimpleUploadedFile("x.jpg", b"x", content_type="image/jpeg")
        )
    p1 = crear("A")
    p2 = crear("B")
    client.get(reverse("catalog:agregar_carrito", args=[p1.id]))
    client.get(reverse("catalog:agregar_carrito", args=[p2.id]))
    assert set(client.session["carrito"]) == {p1.id, p2.id}

@pytest.mark.django_db
def test_carrito_muestra_total_correcto(client):
    User.objects.create_user(username="admin", password="admin123")
    client.login(username="admin", password="admin123")
    p1 = Product.objects.create(name="A", description="d", price=3000, image="x.jpg")
    p2 = Product.objects.create(name="B", description="d", price=2000, image="x.jpg")

    # Forma correcta de modificar sesión
    session = client.session
    session["carrito"] = [p1.id, p2.id]
    session.save()

    response = client.get(reverse("catalog:carrito"))

    contenido = response.content.decode()

    # Verificar que el total aparece correctamente
    assert "5000" in contenido or "$5000" in contenido
