from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from happyhuapi import views
from catalog import views as catalog_views

urlpatterns = [
    # ADMIN
    path('admin/', admin.site.urls),

    # 🛠️ Edición de reservas (solo admin)
    path("booking/<int:pk>/editar/", views.editar_reserva, name="editar_reserva"),

    # 🌐 PÁGINAS PRINCIPALES
    path('', views.Inicio, name='Inicio'),
    path('Catalogo/', views.Catalogo, name='Catalogo'),
    path('Reservar/', views.Reservar, name='Reservar'),
    path('Reservas/', views.Reservas, name='Reservas'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # 🔐 LOGIN / LOGOUT
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 👤 REGISTRO
    path('registro/', views.registro, name='registro'),

    # 🛍️ CATALOGO (namespace catalog)
    path('catalog/', include(('catalog.urls', 'catalog'), namespace='catalog')),

    # 📊 EXPORTAR RESERVAS
    path('exportar_reservas/', views.exportar_reservas, name='exportar_reservas'),

    # 🔄 ACTUALIZAR ESTADO (solo admin)
    path('reservas/<int:pk>/estado/', views.actualizar_estado, name='actualizar_estado'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
