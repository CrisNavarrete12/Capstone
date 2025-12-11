import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_login_exitoso(client):
    # Crear usuario de prueba
    User.objects.create_user(username="admin", password="admin123")

    # Intentar iniciar sesión con credenciales correctas
    response = client.post(reverse("login"), {
        "username": "admin",
        "password": "admin123"
    })

    # Si el login es correcto → redirige (código 302)
    assert response.status_code == 302


@pytest.mark.django_db
def test_login_incorrecto(client):
    # Crear usuario de prueba
    User.objects.create_user(username="admin", password="admin123")

    # Intentar iniciar sesión con contraseña incorrecta
    response = client.post(reverse("login"), {
        "username": "admin",
        "password": "wrongpass"
    })

    # Si el login falla → la página se recarga (status 200) y NO redirige
    assert response.status_code == 200
    assert b"usuario" in response.content.lower() or b"error" in response.content.lower()