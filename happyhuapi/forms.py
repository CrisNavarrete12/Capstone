from django import forms
from .models import Booking
from django.contrib.auth.models import User
from catalog.models import Product
from datetime import datetime


# ============================================================
#                 FORMULARIO DE RESERVA 
# ============================================================

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "customer_name",
            "customer_email",
            "customer_phone",
            "event_date",
            "start_time",
            "end_time",
            "location",
            "notes"
        ]

        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "form-control"}),
            "event_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date", "class": "form-control"}
            ),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "products": forms.SelectMultiple(attrs={"class": "form-control", "size": 5}),
        }

    # -------------------- INIT ÚNICO Y CORRECTO --------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        base_hours = [(f"{h:02d}:00", f"{h:02d}:00") for h in range(8, 23)]

        # Fecha desde POST o desde instancia
        event_date = (
            self.data.get("event_date") or
            (self.instance.event_date.strftime("%Y-%m-%d")
             if self.instance and self.instance.event_date else None)
        )

        # Horas originales POR SIEMPRE conservarlas
        original_start = (
            self.instance.start_time.strftime("%H:%M")
            if self.instance and self.instance.start_time else None
        )
        original_end = (
            self.instance.end_time.strftime("%H:%M")
            if self.instance and self.instance.end_time else None
        )

        # -------------------- Sin fecha: cargar todo --------------------
        if not event_date:
            self.fields["start_time"] = forms.ChoiceField(
                choices=base_hours,
                label="Hora inicio",
                initial=original_start
            )
            self.fields["end_time"] = forms.ChoiceField(
                choices=base_hours,
                label="Hora término",
                initial=original_end
            )
            return

        # -------------------- Con fecha: calcular horas ocupadas --------------------
        reservas = Booking.objects.filter(event_date=event_date).exclude(
            pk=self.instance.pk
        ).exclude(status="cancelled")

        ocupadas = set()
        for r in reservas:
            for h in range(r.start_time.hour, r.end_time.hour):
                ocupadas.add(f"{h:02d}:00")

        horas_disponibles = [(h, h) for h, _ in base_hours if h not in ocupadas]

        # Asegurar que las horas actuales estén siempre disponibles
        if original_start and (original_start, original_start) not in horas_disponibles:
            horas_disponibles.append((original_start, original_start))

        if original_end and (original_end, original_end) not in horas_disponibles:
            horas_disponibles.append((original_end, original_end))

        horas_disponibles.sort()

        # Asignación final
        self.fields["start_time"] = forms.ChoiceField(
            label="Hora inicio",
            choices=horas_disponibles,
            initial=original_start
        )
        self.fields["end_time"] = forms.ChoiceField(
            label="Hora término",
            choices=horas_disponibles,
            initial=original_end
        )

        if self.instance and self.instance.event_date:
            self.initial["event_date"] = self.instance.event_date.strftime("%Y-%m-%d")

    # ============================================================
    #       VALIDACIÓN DE CHOQUE DE HORARIO 
    # ============================================================
    def validate_time_overlap(self):
        cleaned = self.cleaned_data
        date = cleaned.get("event_date")
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")

        if not date or not start or not end:
            return

        solapado = Booking.objects.filter(
            event_date=date,
            start_time__lt=end,
            end_time__gt=start,
            status__in=["pending", "approved", "done"]
        )

        # Si se está editando una reserva, excluirla
        if self.instance.pk:
            solapado = solapado.exclude(pk=self.instance.pk)

        if solapado.exists():
            raise forms.ValidationError(
                "Este horario no está disponible. Selecciona otro rango."
            )

    # -------------------- CLEAN ÚNICO Y CORRECTO --------------------
    def clean(self):
        cleaned = super().clean()

        start = cleaned.get("start_time")
        end = cleaned.get("end_time")

        # Si faltan campos, no validar nada todavía
        if not start or not end:
            return cleaned

        # Convertir string a time si es necesario
        if isinstance(start, str):
            try:
                start = datetime.strptime(start, "%H:%M").time()
                cleaned["start_time"] = start
            except:
                return cleaned  # evita crash

        if isinstance(end, str):
            try:
                end = datetime.strptime(end, "%H:%M").time()
                cleaned["end_time"] = end
            except:
                return cleaned

        # Validar inicio < término
        if start >= end:
            raise forms.ValidationError("La hora de inicio debe ser menor a la hora de término.")

        # Validar solapamiento
        self.validate_time_overlap()

        return cleaned


# ============================================================
#            FORMULARIO DE REGISTRO 
# ============================================================

class RegistroForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
