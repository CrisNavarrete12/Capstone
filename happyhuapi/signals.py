from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Booking, Evidence
from .json_hours import remove_reservation_by_booking_id


# Cuando se borra una reserva → borrar del JSON
@receiver(post_delete, sender=Booking)
def booking_deleted(sender, instance, **kwargs):
    remove_reservation_by_booking_id(instance.pk)


# Crear evidencia automáticamente cuando se genera el booking
@receiver(post_save, sender=Booking)
def crear_evidencia_automatica(sender, instance, created, **kwargs):
    if created:
        Evidence.objects.get_or_create(booking=instance)
