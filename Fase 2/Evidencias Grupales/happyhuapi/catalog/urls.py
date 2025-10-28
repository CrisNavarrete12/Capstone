from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.ListaProductosView.as_view(), name='lista'),
    path('producto/<int:pk>/', views.DetalleProductoView.as_view(), name='detalle'),
    path('agregar/', views.CrearProductoView.as_view(), name='agregar'),
    path('producto/<int:pk>/editar/', views.EditarProductoView.as_view(), name='editar'),
    path('producto/<int:pk>/eliminar/', views.EliminarProductoView.as_view(), name='eliminar'),
]