import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_login_view_carga(client):
    assert client.get(reverse("login")).status_code == 200

@pytest.mark.django_db
def test_logout(client):
    user = User.objects.create_user("test","test@test.com","1234")
    client.login(username="test", password="1234")
    response = client.get(reverse("logout"))
    assert response.status_code in (200,302)

@pytest.mark.django_db
def test_admin_necesita_staff(client):
    user = User.objects.create_user("user","x@x.com","1234")
    client.login(username="user", password="1234")
    response = client.get(reverse("catalog:agregar"))
    assert response.status_code == 302

@pytest.mark.django_db
def test_admin_puede_crear_producto(client):
    user = User.objects.create_user("admin","x@x.com","1234", is_staff=True)
    client.login(username="admin", password="1234")
    assert client.get(reverse("catalog:agregar")).status_code == 200

@pytest.mark.django_db
def test_redirige_si_no_autenticado(client):
    response = client.get(reverse("catalog:agregar"))
    assert response.status_code == 302
