from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django import forms

#  Importa correctamente ambos modelos
from catalog.models import Product
from happyhuapi.models import Booking


# ==========================
#  FUNCIONES DEL CARRITO
# ==========================

def agregar_al_carrito(request, pk):
    """Agrega un producto al carrito almacenado en la sesión."""
    carrito = request.session.get('carrito', [])
    carrito.append(pk)
    request.session['carrito'] = carrito
    return redirect('catalog:lista')


def ver_carrito(request):
    """Muestra los productos del carrito y el total."""
    carrito = request.session.get('carrito', [])
    productos = Product.objects.filter(pk__in=carrito)
    total = sum(producto.price for producto in productos)
    return render(request, 'catalog/carrito.html', {
        'productos': productos,
        'total': total
    })


# ==========================
#  CRUD DE PRODUCTOS
# ==========================

class ListaProductosView(ListView):
    model = Product
    template_name = 'catalog/lista_productos.html'
    context_object_name = 'productos'
    paginate_by = 12


class DetalleProductoView(DetailView):
    model = Product
    template_name = 'catalog/detalle_producto.html'


class SoloAdminMixin(UserPassesTestMixin):
    """Restringe el acceso a usuarios administradores."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('login')


class CrearProductoView(SoloAdminMixin, CreateView):
    model = Product
    fields = ['name', 'description', 'image', 'price']
    template_name = 'catalog/formulario_producto.html'
    success_url = reverse_lazy('catalog:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        print(" Producto creado:", self.object.name)
        return response


class EditarProductoView(SoloAdminMixin, UpdateView):
    model = Product
    fields = ['name', 'description', 'image', 'price']
    template_name = 'catalog/formulario_producto.html'
    success_url = reverse_lazy('catalog:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        print("✏ Producto actualizado:", self.object.name)
        return response


class EliminarProductoView(SoloAdminMixin, DeleteView):
    model = Product
    template_name = 'catalog/confirmar_eliminar_producto.html'
    success_url = reverse_lazy('catalog:lista')


# ==========================
# 📅 CALENDARIO DE RESERVAS (SOLO ADMIN)
# ==========================

def es_admin(user):
    """Función auxiliar para verificar si el usuario es admin."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(es_admin)
def calendario_view(request):
    """Renderiza la vista del calendario (solo visible para administradores)."""
    return render(request, 'catalog/calendario.html')


@user_passes_test(es_admin)
def obtener_reservas_json(request):
    """
    Devuelve todas las reservas en formato JSON para el calendario del admin,
    incluyendo productos asociados, estado en español y formato ISO completo.
    """
    reservas = Booking.objects.all().prefetch_related('products')
    eventos = []

    # 🎨 Colores según estado
    colores_estado = {
        "pending": "#ffc107",    # Amarillo
        "approved": "#198754",   # Verde
        "cancelled": "#dc3545",  # Rojo
        "done": "#0d6efd",       # Azul
    }

    # 🗣️ Traducción de estado al español
    traduccion_estado = {
        "pending": "Pendiente",
        "approved": "Aprobada",
        "cancelled": "Cancelada",
        "done": "Realizada",
    }

    for r in reservas:
        estado = getattr(r, "status", "").lower()
        color = colores_estado.get(estado, "#6610f2")
        estado_es = traduccion_estado.get(estado, "—")

        # 🛒 Productos asociados
        productos = [p.name for p in r.products.all()] if hasattr(r, "products") else []

        eventos.append({
            "id": r.id,
            "title": f"{r.customer_name} ({r.location or '—'}) · {estado_es}",
            "start": f"{r.event_date}T{r.start_time.strftime('%H:%M:%S')}",
            "end": f"{r.event_date}T{r.end_time.strftime('%H:%M:%S')}",
            "backgroundColor": color,
            "borderColor": color,
            "allDay": False,
            "extendedProps": {
                "cliente": r.customer_name,
                "email": r.customer_email,
                "telefono": r.customer_phone,
                "lugar": r.location,
                "estado": estado_es,
                "productos": productos,
                "notas": r.notes,
            },
        })

    return JsonResponse(eventos, safe=False)


# ==========================
# ✏️ EDICIÓN DE RESERVAS DESDE CALENDARIO (SOLO ADMIN)
# ==========================

@user_passes_test(es_admin)
def editar_booking_admin(request, pk):
    """Permite al admin editar una reserva desde el calendario."""
    reserva = get_object_or_404(Booking, pk=pk)

    class BookingForm(forms.ModelForm):
        class Meta:
            model = Booking
            fields = [
                'customer_name', 'customer_email', 'customer_phone',
                'event_date', 'start_time', 'end_time',
                'location', 'notes'
            ]
            widgets = {
                'event_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
                'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
                'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
                'customer_email': forms.EmailInput(attrs={'class': 'form-control'}),
                'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
                'location': forms.TextInput(attrs={'class': 'form-control'}),
                'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            }

        def clean_event_date(self):
            """
            ⚙️ Si no se envía fecha, conserva la existente.
            """
            data = self.cleaned_data.get("event_date")
            if not data and self.instance and self.instance.pk:
                return self.instance.event_date
            return data

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=reserva)
        if form.is_valid():
            reserva_actualizada = form.save(commit=False)
            # ⏰ Mantiene formato 24h uniforme
            reserva_actualizada.start_time = reserva_actualizada.start_time.replace(second=0)
            reserva_actualizada.end_time = reserva_actualizada.end_time.replace(second=0)
            reserva_actualizada.save()
            form.save_m2m()
            return redirect('catalog:calendario')
    else:
        form = BookingForm(instance=reserva)

    return render(request, 'catalog/editar_booking.html', {
        'form': form,
        'reserva': reserva
    })
