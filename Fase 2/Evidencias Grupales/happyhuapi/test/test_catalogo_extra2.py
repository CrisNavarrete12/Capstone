import pytest
from django.urls import reverse
from catalog.models import Product

@pytest.mark.django_db
def test_lista_paginacion(client):
    for i in range(15):
        Product.objects.create(name=f"Prod {i}", description="x", price=100, image="x.jpg")
    response = client.get(reverse("catalog:lista"))
    assert response.status_code == 200
    assert len(response.context["productos"]) <= 12  # paginate_by=12

@pytest.mark.django_db
def test_detalle_producto_html_incluye_nombre(client):
    p = Product.objects.create(name="Producto Prueba", description="x", price=10, image="x.jpg")
    response = client.get(reverse("catalog:detalle", args=[p.id]))
    assert "Producto Prueba" in response.content.decode()

@pytest.mark.django_db
def test_editar_producto_form_renderiza(client):
    p = Product.objects.create(name="Prod", description="x", price=10, image="x.jpg")
    response = client.get(reverse("catalog:editar", args=[p.id]))
    assert response.status_code in (200, 302)
