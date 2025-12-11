# signals.py (nuevo archivo opcional)
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Booking
from .json_hours import remove_reservation_by_booking_id

@receiver(post_delete, sender=Booking)
def booking_deleted(sender, instance, **kwargs):
    remove_reservation_by_booking_id(instance.pk)
