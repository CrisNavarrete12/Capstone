import json
import os
from django.conf import settings
from django.contrib.auth import logout
from .json_hours import add_reservation, remove_reservation_by_booking_id
from django.db import IntegrityError
from datetime import date, timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import redirect

from .models import Booking
from .forms import BookingForm


# PAGINAS PUBLICAS BASICAS

def Inicio(request):
    return render(request, 'Inicio.html')

def Catalogo(request):
    return render(request, 'Catalogo.html')

def Formulario(request):
    return render(request, 'Formulario.html')

def login(request):
    return render(request, 'login.html')



# DASHBOARD SOLO ADMIN

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    return render(request, "dashboard.html")


# UTILIDAD: FECHA LOCAL HOY

def _today_local():
    """
    Si tienes TIME_ZONE='America/Santiago' y USE_TZ=True,
    usamos la fecha local del servidor; si no, date.today()
    """
    try:
        return timezone.localdate()
    except Exception:
        return date.today()


# CALENDARIO (PROXIMOS DIAS)

def Calendario(request):
    """
    Muestra próximos N días (7..31) con las reservas del día.
    Simple y sin JS para ver disponibilidad.
    """
    days = int(request.GET.get("days", 14))
    days = max(7, min(days, 31))  # entre 7 y 31 días

    start = _today_local()
    fechas = [start + timedelta(days=i) for i in range(days)]
    reservas = (
        Booking.objects
        .filter(event_date__in=fechas)
        .exclude(status='cancelled')
        .order_by("event_date", "start_time")
    )

    # Agrupar por día
    by_day = {d: [] for d in fechas}
    for r in reservas:
        by_day[r.event_date].append(r)

    ctx = {"fechas": fechas, "by_day": by_day}
    return render(request, "Calendario.html", ctx)


# RESERVA (FORMULARIO PUBLICO)

def Reservar(request):
    """
    Crea una reserva 'pending' si no hay choque.
    Usa Booking.clean() y save() (con full_clean) para validar.
    Permite pre-cargar fecha/hora con ?date=YYYY-MM-DD&start=HH:MM&end=HH:MM
    """
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            try:
                # Valida reglas del modelo (horarios y solapes)
                booking.full_clean()
            except ValidationError as e:
                if hasattr(e, "messages"):
                    for msg in e.messages:
                        form.add_error(None, msg)
                else:
                    form.add_error(None, getattr(e, "message", "Error de validación."))
            else:
                booking.status = 'pending'
                booking.save()
            try:
                # booking.event_date es un date; lo convertimos a YYYY-MM-DD
                date_str = booking.event_date.isoformat()
                start = booking.start_time.strftime("%H:%M")
                end = booking.end_time.strftime("%H:%M")
                add_reservation(date_str, start, end, booking_id=booking.pk)
            except ValueError as e:
                # Si JSON detecta solapamiento, revertir la reserva (eliminarla) y mostrar error
                booking.delete()
                form.add_error(None, f"No se pudo guardar en la base JSON: {str(e)}")
            except Exception as e:
                # Fallo inesperado: loggear y conservar la reserva (o decidir revertir)
                # aqui revertimos para mantener consistencia entre DB y JSON
                booking.delete()
                form.add_error(None, f"Error al actualizar DB JSON: {str(e)}")
            else:
                messages.success(request, "¡Reserva enviada! Te confirmaremos por correo.")
                return redirect("Calendario")
    
        else:
            messages.error(request, "Revisa los errores del formulario.")
    else:
        initial = {}
        if request.GET.get("date"):
            initial["event_date"] = request.GET.get("date")
        if request.GET.get("start"):
            initial["start_time"] = request.GET.get("start")
        if request.GET.get("end"):
            initial["end_time"] = request.GET.get("end")
        form = BookingForm(initial=initial)

    return render(request, "Reservar.html", {"form": form})


# DETALLE DE RESERVA

def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "booking_detail.html", {"booking": booking})


# LISTADO DE RESERVAS

def Reservas(request):
    """
    Listado de reservas guardadas (excluye canceladas).
    """
    qs = Booking.objects.exclude(status='cancelled').order_by("-event_date", "-start_time")
    paginator = Paginator(qs, 20)  # 20 reservas por pagina
    page = request.GET.get("page")
    reservas = paginator.get_page(page)
    return render(request, "Reservas.html", {"reservas": reservas})
    

# Ruta absoluta del archivo JSON
HOURS_DB_PATH = os.path.join(settings.BASE_DIR, 'data', 'hours_db.json')

# Leer los datos
def load_hours():
    if not os.path.exists(HOURS_DB_PATH):
        return {}
    with open(HOURS_DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# Guardar los datos
def save_hours(data):
    with open(HOURS_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def logout_view(request):
    logout(request)
    return redirect('Inicio')


    

