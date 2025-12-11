import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_usuario_normal_no_ve_agregar_producto(client):
    user = User.objects.create_user("user","u@u.com","1234")
    client.login(username="user", password="1234")
    response = client.get(reverse("catalog:agregar"))
    assert response.status_code == 302  # redirige

@pytest.mark.django_db
def test_admin_si_ve_agregar_producto(client):
    admin = User.objects.create_user("admin","a@a.com","1234", is_staff=True)
    client.login(username="admin", password="1234")
    response = client.get(reverse("catalog:agregar"))
    assert response.status_code == 200
    assert "form" in response.content.decode().lower()
