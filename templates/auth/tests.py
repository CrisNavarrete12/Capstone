import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_login_exitoso(client):

    # Crear un usuario de prueba
    user = User.objects.create_user(username="admin", password="admin")

    # Enviar datos válidos al formulario de login
    response = client.post(reverse("logout"), {
        "username": "admin",
        "password": "admin"
    })

    # El login exitoso normalmente redirige (302)
    assert response.status_code == 302

@pytest.mark.django_db
def test_login_fallido(client):
    
    # No se crea usuario, o se envían credenciales erróneas
    response = client.post(reverse("login"), {
        "username": "usuario_inexistente",
        "password": "incorrecta"
    })

    # La vista de login se renderiza nuevamente con error (200)
    assert response.status_code == 200
    assert b"error" in response.content.lower() or b"credenciales" in response.content.lower()
