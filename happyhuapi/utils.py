from django.core.mail import send_mail

def enviar_correo_aprobacion(booking):
    subject = "¡Tu reserva fue aprobada!"
    message = f"Hola {booking.customer_name}, tu reserva para el día {booking.event_date} fue aprobada."
    from_email = "tu_correo@gmail.com"  # Usa tu correo configurado en settings
    recipient_list = [booking.customer_email]

    send_mail(subject, message, from_email, recipient_list)
def is_admin(user):
    return user.is_staff or user.is_superuser
