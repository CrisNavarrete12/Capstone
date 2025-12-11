import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from catalog.models import Product
from django.core.exceptions import ValidationError

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

@pytest.mark.django_db
def test_crear_producto_sin_imagen():
    product = Product.objects.create(
        name="Producto sin imagen",
        description="desc",
        price=1500
    )
    assert product.id is not None
    assert product.image == ""

@pytest.mark.django_db
def test_precio_producto_no_negativo():
    product = Product(
        name="Negativo",
        description="x",
        price=-2000
    )
    with pytest.raises(ValidationError):
        product.full_clean()

@pytest.mark.django_db
def test_busqueda_simulada_productos():
    Product.objects.create(name="Helado", description="x", price=100)
    Product.objects.create(name="Chocolate", description="x", price=200)

    resultados = Product.objects.filter(name__icontains="cho")
    assert len(resultados) == 1
    assert resultados[0].name == "Chocolate"

@pytest.mark.django_db
def test_lista_usa_template_correcto(client):
    response = client.get(reverse("catalog:lista"))
    assert "catalog/lista_productos.html" in [t.name for t in response.templates]



