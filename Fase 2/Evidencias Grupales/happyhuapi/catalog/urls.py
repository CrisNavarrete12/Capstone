# catalog/urls.py
from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    # PRODUCTOS
    path("", views.ListaProductosView.as_view(), name="lista"),
    path("producto/<int:pk>/", views.DetalleProductoView.as_view(), name="detalle"),
    path("crear/", views.CrearProductoView.as_view(), name="crear"),
    path("editar/<int:pk>/", views.EditarProductoView.as_view(), name="editar"),
    path("eliminar/<int:pk>/", views.EliminarProductoView.as_view(), name="eliminar"),

    #  Alias para compatibilidad con los tests
    path("agregar/", views.CrearProductoView.as_view(), name="agregar"),

    #  CARRITO
    path("carrito/", views.ver_carrito, name="carrito"),
    path("agregar/<int:pk>/", views.agregar_al_carrito, name="agregar_carrito"),


    #  CALENDARIO DE RESERVAS (solo admin)
    path("calendario/", views.calendario_view, name="calendario"),
    path("reservas-json/", views.obtener_reservas_json, name="reservas_json"),
    path("booking/<int:pk>/editar/", views.editar_booking_admin, name="editar_booking_admin"),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
