from django.db import models
from datetime import time as _time
from django.core.exceptions import ValidationError


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to='catalog_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("La hora de inicio debe ser menor a la hora de término.")
        if self.start_time.minute != 0 or self.end_time.minute != 0:
            raise ValidationError("Las horas deben ser en punto (minutos = 00).")
        if self.start_time == _time(0, 0) or self.end_time == _time(0, 0):
            raise ValidationError("No se permiten reservas a medianoche (00:00).")

    def __str__(self):
        return f"{self.event_date} {self.start_time.strftime('%H:%M')} · {self.customer_name}"
