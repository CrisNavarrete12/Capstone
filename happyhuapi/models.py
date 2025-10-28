from django.db import models
from django.core.exceptions import ValidationError
from datetime import time as _time
from django.urls import reverse

class Cliente(models.Model):
    rut = models.CharField(primary_key=True, max_length=10, verbose_name='Rut')
    nombre = models.CharField(max_length=50, blank=True, verbose_name='Nombre')
    correo = models.EmailField(max_length=50, blank=True, verbose_name='Correo')
    direccion = models.CharField(max_length=50, blank=True, verbose_name='Direccion')
    telefono = models.CharField(max_length=15, blank=True, verbose_name='Telefono')

    def __str__(self):
        return self.rut


class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('cancelled', 'Cancelada'),
    ]

    customer_name = models.CharField("Nombre cliente", max_length=120)
    customer_email = models.EmailField("Email")
    customer_phone = models.CharField("Teléfono", max_length=30, blank=True)
    event_date = models.DateField("Fecha del evento")
    start_time = models.TimeField("Hora inicio")
    end_time = models.TimeField("Hora término")
    location = models.CharField("Lugar", max_length=200, blank=True)
    notes = models.TextField("Notas", blank=True)
    status = models.CharField("Estado", max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["event_date", "start_time"]

    def __str__(self):
        return f"{self.event_date} {self.start_time}-{self.end_time} · {self.customer_name}"

    def clean(self):
        # Hora de inicio menor a hora de termino
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("La hora de inicio debe ser menor a la hora de término.")

        # Solo horas exactas (minutos = 00)
        if self.start_time and self.start_time.minute != 0:
            raise ValidationError("La hora de inicio debe ser en punto (minutos = 00).")
        if self.end_time and self.end_time.minute != 0:
            raise ValidationError("La hora de término debe ser en punto (minutos = 00).")

        # No permitir medianoche (00:00)
        midnight = _time(0, 0)
        if self.start_time == midnight or self.end_time == midnight:
            raise ValidationError("No se permiten reservas a las 00:00 (medianoche).")

        # Evitar choques con otras reservas (mismo dia y no canceladas)
        if self.event_date:
            qs = Booking.objects.filter(event_date=self.event_date).exclude(pk=self.pk).exclude(status='cancelled')
            for b in qs:
                if (self.start_time < b.end_time) and (self.end_time > b.start_time):
                    raise ValidationError("Ese horario ya está reservado. Elige otra hora.")

    def save(self, *args, **kwargs):
        # Ejecutar validaciones antes de guardar
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("booking_detail", args=[self.pk])

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price_clp = models.PositiveIntegerField()
    photo = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
