import pytest
import os
import shutil
from datetime import date, time
from django.test import override_settings
from django.core.files.storage import default_storage
from PIL import Image
from happyhuapi.models import Booking
from happyhuapi.utils_qr import generar_qr_para_reserva

@override_settings(
    MEDIA_ROOT="test_media/",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage"
)
@pytest.mark.django_db
def test_qr_generado_y_asignado():
    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="ana@test.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )

    generar_qr_para_reserva(b)
    b.refresh_from_db()

    assert b.qr_image.name.endswith(".png")
    assert default_storage.exists(b.qr_image.name)

@override_settings(MEDIA_ROOT="test_media/")
@pytest.mark.django_db
def test_qr_crea_directorio_automaticamente():
    # eliminar carpeta antes de la prueba
    shutil.rmtree("test_media/", ignore_errors=True)

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="ana@test.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )

    generar_qr_para_reserva(b)

    assert os.path.isdir("test_media/qr_codes")

@override_settings(MEDIA_ROOT="test_media/")
@pytest.mark.django_db
def test_qr_retorna_ruta_valida():
    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="ana@test.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(9,0),
        end_time=time(10,0),
        location="Local"
    )

    ruta = generar_qr_para_reserva(b)

    assert isinstance(ruta, str)
    assert ruta.endswith(".png")

@pytest.mark.django_db
def test_qr_booking_sin_id_lanza_error():
    b = Booking(
        customer_name="Ana",
        customer_email="ana@test.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )

    with pytest.raises(Exception):
        generar_qr_para_reserva(b)

@override_settings(
    MEDIA_ROOT="test_media/",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage"
)
@pytest.mark.django_db
def test_qr_se_reemplaza_correctamente():
    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="ana@test.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )

    ruta1 = generar_qr_para_reserva(b)
    ruta2 = generar_qr_para_reserva(b)

    assert ruta1 != ruta2
    assert b.qr_image.name.endswith(".png")

@override_settings(
    MEDIA_ROOT="test_media/",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage"
)
@pytest.mark.django_db
def test_qr_archivo_es_imagen_valida():
    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="ana@test.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(10,0),
        end_time=time(11,0),
        location="Local"
    )

    generar_qr_para_reserva(b)
    b.refresh_from_db()

    img = Image.open(b.qr_image.path)

    assert img.width > 0
    assert img.height > 0

@override_settings(MEDIA_ROOT="test_media/")
@pytest.mark.django_db
def test_qr_no_elimina_archivos_previos():
    # crear archivo viejo simulado
    os.makedirs("test_media/qr_codes/", exist_ok=True)
    with open("test_media/qr_codes/falso.png", "wb") as f:
        f.write(b"xxx")

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="ana@test.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(8,0),
        end_time=time(9,0),
        location="Local"
    )

    generar_qr_para_reserva(b)

    assert os.path.exists("test_media/qr_codes/falso.png")

@override_settings(MEDIA_ROOT="test_media/")
@pytest.mark.django_db
def test_qr_se_guarda_en_directorio_correcto():
    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="ana@test.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(9,0),
        end_time=time(10,0),
        location="Local"
    )

    generar_qr_para_reserva(b)
    b.refresh_from_db()

    assert b.qr_image.name.startswith("qr_codes/")


@override_settings(MEDIA_ROOT="test_media/")
@pytest.mark.django_db
def test_qr_no_modifica_otro_estado():
    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="ana@test.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(9,0),
        end_time=time(10,0),
        location="Local",
        status="approved"
    )

    generar_qr_para_reserva(b)
    b.refresh_from_db()

    assert b.status == "approved"

@override_settings(MEDIA_ROOT="test_media/")
@pytest.mark.django_db
def test_qr_con_booking_con_productos():
    from catalog.models import Product

    p = Product.objects.create(name="Pack", description="x", price=1000)

    b = Booking.objects.create(
        customer_name="Ana",
        customer_email="ana@test.com",
        customer_phone="123",
        event_date=date.today(),
        start_time=time(9,0),
        end_time=time(10,0),
        location="Local"
    )

    b.products.add(p)

    generar_qr_para_reserva(b)
    b.refresh_from_db()

    assert b.qr_image.name.endswith(".png")

