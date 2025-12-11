import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from catalog.models import Product

@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
@pytest.mark.django_db
def test_agregar_producto_al_carrito(client):
    # Crear imagen falsa
    imagen_fake = SimpleUploadedFile(
        name="planta.jpg",
        content=b"fake-image",
        content_type="image/jpeg"
    )

    # Crear producto de prueba
    product = Product.objects.create(
        name="Planta Aloe Vera",
        description="Planta de interior resistente",
        price=5000,
        image=imagen_fake
    )

    # Hacer la solicitud a la vista
    url = reverse("catalog:agregar_carrito", args=[product.id])
    response = client.get(url)

    # Obtener carrito desde sesión
    carrito = client.session.get("carrito", [])

    # Verificaciones
    assert len(carrito) == 1              # carrito tiene 1 producto
    assert carrito[0] == product.id       # el producto agregado es el correcto
    assert response.status_code in (200, 302)
