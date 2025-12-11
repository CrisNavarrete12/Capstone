from django import forms
from .models import Booking
from django.contrib.auth.models import User
from catalog.models import Product


# ------------------- FORMULARIO DE RESERVA -------------------

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "customer_name", "customer_email", "customer_phone",
            "event_date", "start_time", "end_time",
            "location", "notes"
        ]
        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "form-control"}),
            "customer_email": forms.EmailInput(attrs={"class": "form-control"}),
            "customer_phone": forms.TextInput(attrs={"class": "form-control"}),

            # Campo fecha: formato correcto + evita borrado
            "event_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "class": "form-control",
                    # si quieres impedir que se edite, descomenta esta línea:
                    # "readonly": "readonly",
                }
            ),

            "start_time": forms.TimeInput(
                format="%H:%M",
                attrs={"type": "time", "class": "form-control", "step": "3600"}
            ),
            "end_time": forms.TimeInput(
                format="%H:%M",
                attrs={"type": "time", "class": "form-control", "step": "3600"}
            ),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        event_date = self.data.get("event_date")

        base_hours = [(f"{h:02d}:00", f"{h:02d}:00") for h in range(8, 23)]

        if not event_date:
            self.fields["start_time"] = forms.ChoiceField(choices=base_hours, label="Hora inicio")
            self.fields["end_time"] = forms.ChoiceField(choices=base_hours, label="Hora término")
            return

        reservas = Booking.objects.filter(event_date=event_date).exclude(status='cancelled')

        ocupadas = set()
        for r in reservas:
            for h in range(r.start_time.hour, r.end_time.hour):
                ocupadas.add(f"{h:02d}:00")

        horas_disponibles = [(h, h) for (h, _) in base_hours if h not in ocupadas]

        self.fields["start_time"] = forms.ChoiceField(choices=horas_disponibles, label="Hora inicio")
        self.fields["end_time"] = forms.ChoiceField(choices=horas_disponibles, label="Hora término")

        # Si la instancia tiene fecha, la mostramos correctamente formateada
        if self.instance and self.instance.event_date:
            self.initial["event_date"] = self.instance.event_date.strftime("%Y-%m-%d")

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")

        # Validación de rango horario
        if start and end and start >= end:
            raise forms.ValidationError("La hora de inicio debe ser menor a la hora de término.")
        return cleaned

    def clean_event_date(self):
        """
        Previene que se borre la fecha si no se envía en el POST.
        Conserva la fecha existente en la instancia.
        """
        data = self.cleaned_data.get("event_date")
        if not data and self.instance and self.instance.pk:
            return self.instance.event_date
        return data


# ------------------- FORMULARIO DE REGISTRO -------------------

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
