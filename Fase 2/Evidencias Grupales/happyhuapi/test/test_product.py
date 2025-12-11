import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from catalog.models import Product

# Usaremos FileSystemStorage temporal en tests
@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
@pytest.mark.django_db
def test_crear_producto():
    imagen_fake = SimpleUploadedFile(
        name="planta.jpg",
        content=b"fake-image-content",
        content_type="image/jpeg"
    )

    producto = Product.objects.create(
        name="Suculenta Jade",
        description="Planta pequeña y fácil de cuidar",
        price=3500,
        image=imagen_fake
    )

    assert Product.objects.count() == 1
    assert producto.name == "Suculenta Jade"
    assert producto.price == 3500
