from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from happyhuapi import views
from catalog import views as catalog_views
from .views import iniciar_pago
from happyhuapi.views_evidence import guardar_notas

# IMPORTAR TODAS LAS VISTAS DE EVIDENCIA
from happyhuapi.views_evidence import (
    evidencia_qr_view,
    registrar_llegada,
    registrar_salida,
    subir_foto_evidencia,
    actualizar_checklist,
    evidencia_admin_view,
    evidencia_pdf,
    finalizar_evidencia,
)

urlpatterns = [

    path('admin/', admin.site.urls),

    # PRINCIPAL
    path('', views.Inicio, name='Inicio'),
    path('Catalogo/', views.Catalogo, name='Catalogo'),
    path('Reservar/', views.Reservar, name='Reservar'),
    path('Reservas/', views.Reservas, name='Reservas'),

    # PAGO
    path("pago/", iniciar_pago, name="iniciar_pago"),
    path("pago/exito/", views.pago_exito, name="pago_exito"),

    # LOGIN / LOGOUT
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # REGISTRO
    path('registro/', views.registro, name='registro'),

    # CATALOGO
    path('catalog/', include(('catalog.urls', 'catalog'), namespace='catalog')),

    # EXPORTAR EXCEL
    path('exportar_reservas/', views.exportar_reservas, name='exportar_reservas'),

    # ACTUALIZAR ESTADO
    path('reservas/<int:pk>/estado/', views.actualizar_estado, name='actualizar_estado'),

    # RESET PASSWORD
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name="auth/password_reset.html"), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="auth/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="auth/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="auth/password_reset_complete.html"), name="password_reset_complete"),

    # RUTAS QR 
    path("evidencia/<int:booking_id>/qr/", evidencia_qr_view, name="evidencia_qr"),

    # ACCIONES DEL TRABAJADOR
    path("evidencia/<int:booking_id>/llegada/", registrar_llegada, name="registrar_llegada"),
    path("evidencia/<int:booking_id>/salida/", registrar_salida, name="registrar_salida"),
    path("evidencia/<int:booking_id>/foto/", subir_foto_evidencia, name="subir_foto_evidencia"),
    path("evidencia/<int:booking_id>/checklist/", actualizar_checklist, name="actualizar_checklist"),
    path("evidencia/<int:booking_id>/notas/", guardar_notas, name="guardar_notas"),


    # ADMIN
    path("booking/<int:pk>/editar/", views.editar_reserva, name="editar_reserva"),

    # AGREGAR PRODUCTO
    path("booking/<int:booking_id>/add/<int:product_id>/", 
         views.agregar_producto, 
         name="add_product"),

    # QUITAR PRODUCTO
    path("booking/<int:booking_id>/remove/<int:product_id>/", 
         views.quitar_producto, 
         name="remove_product"),

    # ELIMINAR DESDE EL MODAL
    path("booking/<int:booking_id>/producto/<int:product_id>/eliminar/",
         views.eliminar_producto_reserva,
         name="eliminar_producto_reserva"),

    # ADMIN VER PDF
    path("evidencia/<int:booking_id>/admin/", evidencia_admin_view, name="evidencia_admin"),
    path("evidencia/<int:booking_id>/pdf/", evidencia_pdf, name="evidencia_pdf"),
    path("evidencia/<int:booking_id>/finalizar/", finalizar_evidencia, name="finalizar_evidencia"),
    path("sobre-nosotros/", views.sobre_nosotros, name="sobre_nosotros"),
    path("contacto/", views.contacto, name="Contacto"),

]

# MEDIA
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
