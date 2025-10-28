from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Product

# Vistas para usuarios (ver catálogo) 
class ListaProductosView(ListView):
    model = Product
    template_name = 'catalog/lista_productos.html'
    context_object_name = 'productos'
    paginate_by = 12

class DetalleProductoView(DetailView):
    model = Product
    template_name = 'catalog/detalle_producto.html'

# Mixin para restringir acceso solo a administradores
class SoloAdminMixin(UserPassesTestMixin):
    """Permite acceso solo a usuarios autenticados con permisos de administrador (staff)."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        from django.shortcuts import redirect
        return redirect('login')

# CRUD solo para administradores 
class CrearProductoView(SoloAdminMixin, CreateView):
    model = Product
    fields = ['name', 'description', 'image']
    template_name = 'catalog/formulario_producto.html'
    success_url = reverse_lazy('catalog:lista')

class EditarProductoView(SoloAdminMixin, UpdateView):
    model = Product
    fields = ['name', 'description', 'image']
    template_name = 'catalog/formulario_producto.html'
    success_url = reverse_lazy('catalog:lista')

class EliminarProductoView(SoloAdminMixin, DeleteView):
    model = Product
    template_name = 'catalog/confirmar_eliminar_producto.html'
    success_url = reverse_lazy('catalog:lista')
