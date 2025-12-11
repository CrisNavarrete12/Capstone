from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Booking, Evidence, EvidencePhoto


# ==========================
# FOTOS DE EVIDENCIA INLINE
# ==========================
class EvidencePhotoInline(admin.TabularInline):
    model = EvidencePhoto
    extra = 0
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="120" style="border-radius:6px;" />',
                obj.image.url
            )
        return "—"

    preview.short_description = "Vista previa"


# ==========================
# EVIDENCIA (ADMIN)
# ==========================
@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ("booking", "arrival_time", "finish_time", "last_updated")
    search_fields = ("booking__customer_name",)
    list_filter = ("arrival_time", "finish_time")
    inlines = [EvidencePhotoInline]


# ==========================
# RESERVAS (BOOKING)
# ==========================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = (
        "event_date", "start_time", "end_time",
        "customer_name", "status",
        "ver_en_sitio",
        "ver_evidencia",
        "ver_pdf",
    )
    list_filter   = ("event_date", "status")
    search_fields = ("customer_name", "customer_email", "location", "notes")
    ordering      = ("event_date", "start_time")
    readonly_fields = ("created_at",)
    list_per_page = 25

    # ------------------------------
    # Editar reserva
    # ------------------------------
    def ver_en_sitio(self, obj):
        try:
            url = reverse("editar_reserva", args=[obj.pk])
            return format_html(
                '<a href="{}" target="_blank" '
                'style="color:#0d6efd; font-weight:600;">📝 Editar</a>',
                url
            )
        except Exception:
            return "—"
    ver_en_sitio.short_description = "Editar"

    # ------------------------------
    # Ver evidencia
    # ------------------------------
    def ver_evidencia(self, obj):
        try:
            url = reverse("evidencia_admin", args=[obj.pk])
            return format_html(
                '<a href="{}" target="_blank" '
                'style="color:#6610f2; font-weight:600;">👁 Ver</a>',
                url
            )
        except Exception:
            return "—"
    ver_evidencia.short_description = "Evidencia"

    # ------------------------------
    # Descargar PDF
    # ------------------------------
    def ver_pdf(self, obj):
        try:
            url = reverse("evidencia_pdf", args=[obj.pk])
            return format_html(
                '<a href="{}" target="_blank" '
                'style="color:#198754; font-weight:600;">📄 PDF</a>',
                url
            )
        except Exception:
            return "—"
    ver_pdf.short_description = "Evidencia PDF"
