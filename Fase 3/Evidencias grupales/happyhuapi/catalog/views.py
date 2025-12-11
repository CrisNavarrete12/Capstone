# ==========================
# IMPORTS
# ==========================

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms

# Modelos
from catalog.models import Product
from happyhuapi.models import Booking


# ==========================
# FUNCIONES DEL CARRITO
# ==========================

def agregar_al_carrito(request, pk):
    """Agrega un producto al carrito (sesión)."""
    carrito = request.session.get('carrito', [])
    carrito.append(pk)
    request.session['carrito'] = carrito
    return redirect('catalog:lista')


@login_required
def ver_carrito(request):
    carrito = request.session.get("carrito", [])
    productos = Product.objects.filter(id__in=carrito)

    total = sum(p.price for p in productos)
    deposito = int(total * 0.30)  # cálculo seguro

    return render(request, "carrito.html", {
        "productos": productos,
        "total": total,
        "deposito": deposito
    })
@login_required
def eliminar_del_carrito(request, pk):
    carrito = request.session.get("carrito", [])

    if pk in carrito:
        carrito.remove(pk)

    request.session["carrito"] = carrito
    request.session.modified = True

    return redirect("catalog:carrito")




# ==========================
# CRUD DE PRODUCTOS
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
    """Restringe acceso solo a administradores."""

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
        print("Producto creado:", form.instance.name)
        return super().form_valid(form)


class EditarProductoView(SoloAdminMixin, UpdateView):
    model = Product
    fields = ['name', 'description', 'image', 'price']
    template_name = 'catalog/formulario_producto.html'
    success_url = reverse_lazy('catalog:lista')

    def form_valid(self, form):
        print("Producto actualizado:", form.instance.name)
        return super().form_valid(form)


class EliminarProductoView(SoloAdminMixin, DeleteView):
    model = Product
    template_name = 'catalog/confirmar_eliminar_producto.html'
    success_url = reverse_lazy('catalog:lista')


# ==========================
# CALENDARIO (ADMIN)
# ==========================

def es_admin(user):
    """Verifica que sea admin o superusuario."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(es_admin)
def calendario_view(request):
    """Vista del calendario."""
    return render(request, 'catalog/calendario.html')


@user_passes_test(es_admin)
def obtener_reservas_json(request):
    """Devuelve reservas en JSON para el calendario admin."""
    reservas = Booking.objects.all().prefetch_related('products')
    eventos = []

    colores_estado = {
        "pending": "#ffc107",
        "approved": "#198754",
        "cancelled": "#dc3545",
        "done": "#0d6efd",
    }

    traduccion_estado = {
        "pending": "Pendiente",
        "approved": "Aprobada",
        "cancelled": "Cancelada",
        "done": "Realizada",
    }

    for r in reservas:
        estado = r.status.lower()
        eventos.append({
            "id": r.id,
            "title": f"{r.customer_name} ({r.location or '—'}) · {traduccion_estado.get(estado)}",
            "start": f"{r.event_date}T{r.start_time.strftime('%H:%M:%S')}",
            "end": f"{r.event_date}T{r.end_time.strftime('%H:%M:%S')}",
            "backgroundColor": colores_estado.get(estado, "#6610f2"),
            "borderColor": colores_estado.get(estado, "#6610f2"),
            "allDay": False,
            "extendedProps": {
                "cliente": r.customer_name,
                "email": r.customer_email,
                "telefono": r.customer_phone,
                "lugar": r.location,
                "estado": traduccion_estado.get(estado),
                "productos": [p.name for p in r.products.all()],
                "notas": r.notes,
            },
        })

    return JsonResponse(eventos, safe=False)


# ==========================
# EDICIÓN DE RESERVAS (ADMIN)
# ==========================

@user_passes_test(es_admin)
def editar_booking_admin(request, pk):
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
            data = self.cleaned_data.get("event_date")
            return data or self.instance.event_date

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=reserva)
        if form.is_valid():
            actualizada = form.save(commit=False)
            actualizada.start_time = actualizada.start_time.replace(second=0)
            actualizada.end_time = actualizada.end_time.replace(second=0)
            actualizada.save()
            form.save_m2m()
            return redirect('catalog:calendario')
    else:
        form = BookingForm(instance=reserva)

    return render(request, 'catalog/editar_booking.html', {
        'form': form,
        'reserva': reserva
    })
