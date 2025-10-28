from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Cliente, Booking

admin.site.register(Cliente)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = ("event_date", "start_time", "end_time", "customer_name", "status", "ver_en_sitio")
    list_filter   = ("event_date", "status")
    search_fields = ("customer_name", "customer_email", "location", "notes")
    ordering      = ("event_date", "start_time")

    def get_view_on_site_url(self, obj=None):
        if obj is None:
            return None
        return reverse("booking_detail", args=[obj.pk])

    def ver_en_sitio(self, obj):
        url = reverse("booking_detail", args=[obj.pk])
        return format_html('<a href="{}" target="_blank">Abrir detalle</a>', url)
    ver_en_sitio.short_description = "Detalle público"

