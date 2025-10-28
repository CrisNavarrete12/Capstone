from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from .forms import AdminOnlyAuthForm
from .views import Inicio, Catalogo, Formulario, dashboard
from . import views 

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),
    path('catalog/', include('catalog.urls')),
    
    
    

    # Rutas publicas
    path('', Inicio, name="Inicio"),
    path('Catalogo/', Catalogo, name="Catalogo"),
    
    # Calendario + Reservar (publicos)
    path('Calendario/', views.Calendario, name="Calendario"),
    path('Reservar/', views.Reservar, name="Reservar"),
    # Añade de vuelta (si quitaste esta linea):
    path('Formulario/', Formulario, name="Formulario"),


    # NUEVO: Listado de reservas (todas guardadas en la BD)
    path('Reservas/', views.Reservas, name="Reservas"),

    # Detalle de reserva (para "Ver en el sitio" del admin)
    path('reserva/<int:pk>/', views.booking_detail, name="booking_detail"),

    # Login / Logout solo administradores
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name="auth/login.html",
            authentication_form=AdminOnlyAuthForm,
        ),
        name="login",
    ),
     path('logout/', views.logout_view, name='logout'),

    # Panel interno (solo admin)
    path('dashboard/', dashboard, name="dashboard"),

    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)