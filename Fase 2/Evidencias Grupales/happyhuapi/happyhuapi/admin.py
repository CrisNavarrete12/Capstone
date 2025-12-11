from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Cliente, Booking


# ==========================
# 👥 CLIENTES
# ==========================
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración de Clientes.
    Ajusta dinámicamente los campos si el modelo no tiene 'email' o 'telefono'.
    """
    list_display = ("nombre", "mostrar_correo", "mostrar_telefono")
    search_fields = ("nombre", "customer_email", "customer_phone")

    def mostrar_correo(self, obj):
        """
        Muestra el correo si existe el campo correspondiente.
        """
        return getattr(obj, "customer_email", getattr(obj, "email", "—"))
    mostrar_correo.short_description = "Correo"

    def mostrar_telefono(self, obj):
        """
        Muestra el teléfono si existe el campo correspondiente.
        """
        return getattr(obj, "customer_phone", getattr(obj, "telefono", "—"))
    mostrar_telefono.short_description = "Teléfono"


# ==========================
# 📅 RESERVAS
# ==========================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = (
        "event_date", "start_time", "end_time",
        "customer_name", "status", "ver_en_sitio"
    )
    list_filter   = ("event_date", "status")
    search_fields = ("customer_name", "customer_email", "location", "notes")
    ordering      = ("event_date", "start_time")

    def ver_en_sitio(self, obj):
        """
        🔗 Enlace directo para abrir la edición pública de la reserva (solo admin).
        """
        try:
            url = reverse("editar_reserva", args=[obj.pk])
            return format_html(
                '<a href="{}" class="button" target="_blank" '
                'style="color:#0d6efd; font-weight:600;">📝 Editar Reserva</a>',
                url
            )
        except Exception:
            return "—"

    ver_en_sitio.short_description = "Acceso rápido"

    readonly_fields = ("created_at",)
    list_per_page = 25
