from django import forms
from .models import Booking
from django.core.exceptions import ValidationError
from datetime import time as _time
from django.contrib.auth.forms import AuthenticationForm

class AdminOnlyAuthForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        # Permitir solo administradores (superuser o staff)
        if not (user.is_staff or user.is_superuser):
            raise forms.ValidationError(
                "Solo administradores pueden iniciar sesión.",
                code="no_admin",
            )

class BookingForm(forms.ModelForm):
    HOURS = [(f"{h:02d}:00", f"{h:02d}:00") for h in range(8, 23)]  

    start_time = forms.ChoiceField(choices=HOURS, label="Hora inicio")
    end_time = forms.ChoiceField(choices=HOURS, label="Hora término")
    
    class Meta:
        model = Booking
        fields = [
            "customer_name", "customer_email", "customer_phone",
            "event_date", "start_time", "end_time",
            "location", "notes"
        ]
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        if start and end and start >= end:
            raise forms.ValidationError("La hora de inicio debe ser menor a la de término.")
        midnight = _time(0, 0)
        if start and start.minute != 0:
            raise forms.ValidationError("La hora de inicio debe ser en punto (minutos = 00).")
        if end and end.minute != 0:
            raise forms.ValidationError("La hora de término debe ser en punto (minutos = 00).")
        if start == midnight or end == midnight:
            raise forms.ValidationError("No se permiten reservas a las 00:00 (medianoche).")

        return cleaned
