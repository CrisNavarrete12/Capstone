from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, time as _time
from django.urls import reverse
from catalog.models import Product
from django.contrib.auth.models import User


# ==========================
# 👥 CLIENTE
# ==========================
class Cliente(models.Model):
    rut = models.CharField(primary_key=True, max_length=10, verbose_name='Rut')
    nombre = models.CharField(max_length=50, blank=True, verbose_name='Nombre')
    correo = models.EmailField(max_length=50, blank=True, verbose_name='Correo')
    direccion = models.CharField(max_length=50, blank=True, verbose_name='Dirección')
    telefono = models.CharField(max_length=15, blank=True, verbose_name='Teléfono')

    def __str__(self):
        return f"{self.nombre or 'Sin nombre'} ({self.rut})"


# ==========================
# 🏷️ CATEGORÍA
# ==========================
class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


# ==========================
# 📅 RESERVA
# ==========================
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    total = models.IntegerField(default=0)
    products = models.ManyToManyField(Product, blank=True)

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
    notes = models.TextField("Notas", blank=True)
    status = models.CharField("Estado", max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["event_date", "start_time"]

    def __str__(self):
        return f"{self.event_date} {self.start_time.strftime('%H:%M')}–{self.end_time.strftime('%H:%M')} · {self.customer_name}"

    # 🧩 Validaciones personalizadas
    def clean(self):
        # Asegura que las horas sean tipo time
        if isinstance(self.start_time, str):
            self.start_time = datetime.strptime(self.start_time, "%H:%M").time()
        if isinstance(self.end_time, str):
            self.end_time = datetime.strptime(self.end_time, "%H:%M").time()

        # Validaciones
        if not self.start_time or not self.end_time:
            raise ValidationError("Debes indicar una hora de inicio y término.")
        if self.start_time >= self.end_time:
            raise ValidationError("La hora de inicio debe ser menor a la hora de término.")
        if self.start_time.minute != 0 or self.end_time.minute != 0:
            raise ValidationError("Las horas deben ser en punto (minutos = 00).")
        if self.start_time == _time(0, 0) or self.end_time == _time(0, 0):
            raise ValidationError("No se permiten reservas a las 00:00 (medianoche).")

        # Evita traslapes en la misma fecha
        if self.event_date:
            overlaps = Booking.objects.filter(event_date=self.event_date).exclude(pk=self.pk).exclude(status='cancelled')
            for reserva in overlaps:
                if (self.start_time < reserva.end_time) and (self.end_time > reserva.start_time):
                    raise ValidationError("Ese horario ya está reservado. Elige otra hora.")

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        # Ya no se usa "booking_detail", pero lo dejamos para compatibilidad
        return reverse("editar_reserva", args=[self.pk])


# ==========================
# 🛒 PRODUCTO
# ==========================
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="catalog/", blank=True, null=True)
    price = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def price_clp(self):
        """Muestra el precio con formato CLP."""
        return f"${self.price:,}".replace(",", ".")
