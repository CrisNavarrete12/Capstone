from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, date
from django.urls import reverse
from catalog.models import Product
from django.contrib.auth.models import User
from decimal import Decimal


# ============================================
# RESERVA (BOOKING)
# ============================================
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # Productos agregados desde el catálogo
    products = models.ManyToManyField(Product, blank=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    is_paid = models.BooleanField(default=False)
    payment_token = models.CharField(max_length=200, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    # Imagen QR generada
    qr_image = models.ImageField(upload_to="qr_codes/", null=True, blank=True)

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('done', 'Realizada'),
        ('cancelled', 'Cancelada'),
    ]

    customer_name = models.CharField("Nombre cliente", max_length=120)
    customer_email = models.EmailField("Email")
    customer_phone = models.CharField("Teléfono", max_length=30, blank=True)
    event_date = models.DateField("Fecha del evento")
    start_time = models.TimeField("Hora inicio")
    end_time = models.TimeField("Hora término")
    location = models.CharField("Lugar", max_length=200, blank=True)

    # ⭐ ESTE ES EL CAMPO CORRECTO QUE CONTIENE LAS NOTAS DEL CLIENTE
    notes = models.TextField("Notas", blank=True)

    status = models.CharField("Estado", max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["event_date", "start_time"]

    def __str__(self):
        try:
            start = self.start_time.strftime("%H:%M")
            end = self.end_time.strftime("%H:%M")
        except AttributeError:
            start = self.start_time
            end = self.end_time

        return f"{self.event_date} {start}–{end} · {self.customer_name}"

    # ============================================
    # VALIDACIONES
    # ============================================
    def clean(self):
        errors = {}

        # Convertir horas si vienen como string
        if isinstance(self.start_time, str):
            self.start_time = datetime.strptime(self.start_time, "%H:%M").time()

        if isinstance(self.end_time, str):
            self.end_time = datetime.strptime(self.end_time, "%H:%M").time()

        # Validar existencia de horas
        if self.start_time is None:
            errors["start_time"] = "La hora de inicio es obligatoria."

        if self.end_time is None:
            errors["end_time"] = "La hora de término es obligatoria."

        # Validar minutos exactos (00)
        if self.start_time and self.start_time.minute != 0:
            errors["start_time"] = "Las reservas deben iniciar en una hora exacta (minuto 00)."

        if self.end_time and self.end_time.minute != 0:
            errors["end_time"] = "Las reservas deben terminar en una hora exacta (minuto 00)."

        # Comparación start < end
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                errors["end_time"] = "La hora de término debe ser posterior a la hora de inicio."

        # Validar traslape de horarios
        if self.start_time and self.end_time:
            overlaps = Booking.objects.filter(event_date=self.event_date)\
                                      .exclude(pk=self.pk)\
                                      .exclude(status='cancelled')

            for reserva in overlaps:
                if (self.start_time < reserva.end_time) and (self.end_time > reserva.start_time):
                    errors["start_time"] = "Ese horario ya está reservado. Elige otra hora."
                    break

        # Validación fecha pasada
        if self.event_date < date.today():
            errors["event_date"] = "No puedes crear reservas en fechas pasadas."

        if errors:
            raise ValidationError(errors)

        super().clean()

    # ============================================
    # SAVE (actualiza depósito automáticamente)
    # ============================================
    def save(self, *args, **kwargs):
        if self.total_price:
            self.deposit_amount = int(self.total_price * Decimal("0.30"))

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("editar_reserva", args=[self.pk])


# ============================================
# EVIDENCIA (para trabajadores)
# ============================================
class Evidence(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="evidence"
    )

    arrival_time = models.DateTimeField(null=True, blank=True)
    finish_time = models.DateTimeField(null=True, blank=True)

    table_installed = models.BooleanField(default=False)
    decoration_ready = models.BooleanField(default=False)
    balloons_ready = models.BooleanField(default=False)
    candy_ready = models.BooleanField(default=False)

    notes = models.TextField(blank=True, null=True)

    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Evidencia de {self.booking.customer_name}"


# ============================================
# FOTOS DE EVIDENCIA
# ============================================
class EvidencePhoto(models.Model):
    evidence = models.ForeignKey(
        Evidence,
        related_name="photos",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="evidence_photos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto {self.id} de {self.evidence.booking.customer_name}"
