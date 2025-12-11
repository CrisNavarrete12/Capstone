from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import reverse

from happyhuapi.models import Booking, Evidence, EvidencePhoto


# VALIDACIÓN DE TRABAJADOR 
def es_trabajador(user):
    return user.is_authenticated and user.groups.filter(name="Trabajador").exists()


# VISTA PRINCIPAL QR (TRABAJADOR)
@login_required
def evidencia_qr_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    evidencia, _ = Evidence.objects.get_or_create(booking=booking)

    if not es_trabajador(request.user):
        return render(request, "no_autorizado.html")

    return render(request, "evidencia_trabajador.html", {
        "booking": booking,
        "evidencia": evidencia,
        "photos": evidencia.photos.all(),
    })


# REGISTRAR HORARIOS
@require_POST
@login_required
def registrar_llegada(request, booking_id):
    evidencia = get_object_or_404(Evidence, booking_id=booking_id)

    if not es_trabajador(request.user):
        return JsonResponse({"error": "No autorizado"}, status=403)

    evidencia.arrival_time = timezone.now()
    evidencia.save()
    return JsonResponse({"ok": True, "arrival_time": evidencia.arrival_time})


@require_POST
@login_required
def registrar_salida(request, booking_id):
    evidencia = get_object_or_404(Evidence, booking_id=booking_id)

    if not es_trabajador(request.user):
        return JsonResponse({"error": "No autorizado"}, status=403)

    evidencia.finish_time = timezone.now()
    evidencia.save()
    return JsonResponse({"ok": True, "finish_time": evidencia.finish_time})


# SUBIR FOTO 
@require_POST
@login_required
def subir_foto_evidencia(request, booking_id):
    evidencia = get_object_or_404(Evidence, booking_id=booking_id)

    if not es_trabajador(request.user):
        return JsonResponse({"error": "No autorizado"}, status=403)

    image = request.FILES.get("image")
    if not image:
        return JsonResponse({"error": "No se envió imagen"}, status=400)

    foto = EvidencePhoto.objects.create(evidence=evidencia, image=image)

    return JsonResponse({
        "ok": True,
        "photo_url": foto.image.url
    })


# CHECKLIST (AUTO-SAVE)
@require_POST
@login_required
def actualizar_checklist(request, booking_id):
    evidencia = get_object_or_404(Evidence, booking_id=booking_id)

    if not es_trabajador(request.user):
        return JsonResponse({"error": "No autorizado"}, status=403)

    campo = request.POST.get("campo")
    valor = request.POST.get("valor") == "true"

    if hasattr(evidencia, campo):
        setattr(evidencia, campo, valor)
        evidencia.save()
        return JsonResponse({"ok": True})

    return JsonResponse({"error": "Campo inválido"}, status=400)


# ADMIN VER EVIDENCIA
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def evidencia_admin_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    evidencia = booking.evidence

    return render(request, "evidencia_admin.html", {
        "booking": booking,
        "evidencia": evidencia,
        "photos": evidencia.photos.all(),
    })

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Evidence, Booking

@require_POST
@login_required
def guardar_notas(request, booking_id):
    print("DEBUG → Entró a guardar_notas")
    print("🟦 GUARDAR NOTAS → POST DATA:", request.POST)

    evidencia = get_object_or_404(Evidence, booking_id=booking_id)

    # Aceptar ambos nombres: "notes" y "notas"
    notas = request.POST.get("notes") or request.POST.get("notas") or ""
    notas = notas.strip()

    print("DEBUG → Notas recibidas:", notas)

    evidencia.notes = notas
    evidencia.save()

    return JsonResponse({"ok": True, "msg": "Notas guardadas correctamente"})

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import requests
from io import BytesIO
from reportlab.lib.units import inch


@login_required
def evidencia_pdf(request, booking_id):
    if not (request.user.is_staff or es_trabajador(request.user)):
        return HttpResponse("No autorizado", status=403)

    booking = get_object_or_404(Booking, id=booking_id)
    evidencia = booking.evidence
    photos = evidencia.photos.all()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Evidencia_{booking.customer_name}.pdf"'

    styles = getSampleStyleSheet()
    story = []
    doc = SimpleDocTemplate(response, pagesize=letter)

    story.append(Paragraph("<b>Reporte de Evidencia - HappyHuapi</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>Cliente:</b> {booking.customer_name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Fecha:</b> {booking.event_date}", styles["Normal"]))
    story.append(Paragraph(f"<b>Horario:</b> {booking.start_time} – {booking.end_time}", styles["Normal"]))
    story.append(Spacer(1, 15))

# FORMATEAR FECHAS BONITO
    def fmt(dt):
        try:
            return dt.strftime("%d-%m-%Y %H:%M")
        except:
            return "No registrado"

    story.append(Paragraph("<b>Horarios</b>", styles["Heading2"]))
    story.append(Paragraph(f"Llegada: {fmt(evidencia.arrival_time)}", styles["Normal"]))
    story.append(Paragraph(f"Salida: {fmt(evidencia.finish_time)}", styles["Normal"]))
    story.append(Spacer(1, 15))


    check = lambda x: "✔" if x else "✘"

    story.append(Paragraph("<b>Checklist</b>", styles["Heading2"]))
    story.append(Paragraph(f"Mesa instalada: {check(evidencia.table_installed)}", styles["Normal"]))
    story.append(Paragraph(f"Decoración lista: {check(evidencia.decoration_ready)}", styles["Normal"]))
    story.append(Paragraph(f"Globos inflados: {check(evidencia.balloons_ready)}", styles["Normal"]))
    story.append(Paragraph(f"Candy listo: {check(evidencia.candy_ready)}", styles["Normal"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Notas del trabajador:</b>", styles["Normal"]))
    story.append(Paragraph(evidencia.notes or "—", styles["Normal"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Fotos</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))

    for f in photos:
        try:
            r = requests.get(f.image.url)
            if r.status_code == 200:
                img_data = BytesIO(r.content)
                img = Image(img_data)
                img.drawHeight = 2.5 * inch
                img.drawWidth = 2.5 * inch
                story.append(img)
                story.append(Spacer(1, 10))
        except:
            pass

    doc.build(story)
    return response


# FINALIZAR EVIDENCIA
@require_POST
@login_required
def finalizar_evidencia(request, booking_id):
    evidencia = get_object_or_404(Evidence, booking_id=booking_id)

    if not es_trabajador(request.user):
        return JsonResponse({"error": "No autorizado"}, status=403)

    evidencia.completed = True
    evidencia.completed_at = timezone.now()
    evidencia.save()

    pdf_url = reverse("evidencia_pdf", args=[booking_id])

    return JsonResponse({"ok": True, "pdf_url": pdf_url})
