import pytest
from django.urls import reverse
from catalog.models import Product
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile


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

@pytest.mark.django_db
def test_catalogo_carga(client):
    response = client.get("/Catalogo/")
    assert response.status_code == 302 or response.status_code == 200

@pytest.mark.django_db
def test_detalle_producto(client):
    p = Product.objects.create(name="X", description="d", price=1000)
    response = client.get(f"/catalogo/producto/{p.id}/")
    assert response.status_code in (200, 302, 404)

@pytest.mark.django_db
def test_agregar_dos_veces_mismo_producto(client):
    p = Product.objects.create(name="A", description="d", price=1000)

    # URL correcta (usar reverse SIEMPRE)
    url = reverse("catalog:agregar_carrito", args=[p.id])

    # agregar dos veces
    client.get(url)
    client.get(url)

    carrito = client.session.get("carrito", [])

    # el carrito debe tener 2 elementos iguales
    assert len(carrito) == 2
    assert carrito.count(p.id) == 2 or carrito.count(str(p.id)) == 2


@pytest.mark.django_db
def test_eliminar_producto_carrito(client):
    p = Product.objects.create(name="A", description="d", price=1000)

    client.get(f"/catalogo/agregar/{p.id}/")
    client.get(f"/catalogo/eliminar/{p.id}/")

    carrito = client.session.get("carrito", [])
    assert p.id not in carrito

@pytest.mark.django_db
def test_debug_crear_producto(client):
    admin = User.objects.create_user("admin","a@a.com","1234", is_staff=True)
    client.login(username="admin", password="1234")

    imagen = SimpleUploadedFile("test.jpg", b"xxx", content_type="image/jpeg")

    data = {
        "name": "Nuevo Producto",
        "description": "Desc",
        "price": 1500,
        "image": imagen,
    }

    response = client.post(reverse("catalog:agregar"), data, format="multipart")

    print("\nSTATUS:", response.status_code)

    if hasattr(response, "context") and response.context:
        form = response.context.get("form")
        if form:
            print("\nFORM ERRORS:", form.errors)

    print("\nTEMPLATES:", [t.name for t in response.templates] if hasattr(response, "templates") else "NO TEMPLATE")

    assert True



@pytest.mark.django_db
def test_crear_producto_imagen_invalida(client):
    admin = User.objects.create_user("admin","x@x.com","1234", is_staff=True)
    client.login(username="admin", password="1234")

    archivo = SimpleUploadedFile("archivo.txt", b"noimage", content_type="text/plain")

    data = {
        "name": "Producto Fail",
        "description": "Desc",
        "price": 1000,
        "image": archivo
    }

    response = client.post(reverse("catalog:agregar"), data)

    # La vista debería rechazarlo
    assert response.status_code == 200
    assert not Product.objects.filter(name="Producto Fail").exists()

@pytest.mark.django_db
def test_detalle_producto_inexistente_retorna_404(client):
    response = client.get(reverse("catalog:detalle", args=[9999]))
    assert response.status_code == 404

@pytest.mark.django_db
def test_editar_producto_cambia_descripcion(client):
    admin = User.objects.create_user("admin","a@a.com","1234", is_staff=True)
    client.login(username="admin", password="1234")

    p = Product.objects.create(name="X", description="Vieja", price=100, image="x.jpg")

    response = client.post(reverse("catalog:editar", args=[p.id]), {
        "name": "X",
        "description": "Nueva desc",
        "price": 100
    })

    p.refresh_from_db()
    assert p.description == "Nueva desc"

@pytest.mark.django_db
def test_eliminar_producto_usuario_normal_no_puede(client):
    user = User.objects.create_user("user","u@u.com","1234")
    client.login(username="user", password="1234")

    p = Product.objects.create(name="X", description="d", price=100)

    response = client.post(reverse("catalog:eliminar", args=[p.id]))
    assert response.status_code == 302  # redirige a login
    assert Product.objects.filter(id=p.id).exists()  # sigue existiendo






