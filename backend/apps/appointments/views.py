import json
from datetime import timedelta, time

from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import VetSchedule, TimeSlot, Appointment, WaitingListEntry
from apps.patients.models import Patient, ClinicalRecords


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _vet_display_name(vet):
    """Resolve Veterinarian → ClinicalStaff → User → full name."""
    try:
        user = vet.clinical_staff.user
        return f"{user.first_name} {user.last_name}".strip() or user.email
    except Exception:
        return str(vet)


def _serialize_appointment(appt):
    """Serialize an Appointment to the dict shape the frontend expects."""
    slot = appt.slot
    if slot:
        vet = slot.schedule.vet
        vet_name = _vet_display_name(vet)
        vet_id = vet.id
        date = str(slot.schedule.start_date)
        time_val = str(slot.start_time)
    else:
        vet_name = ""
        vet_id = None
        date = ""
        time_val = ""

    owner = appt.patient.owner
    if owner:
        owner_user = owner.user
        owner_name = f"{owner_user.first_name} {owner_user.last_name}".strip() or owner_user.email
        owner_id = str(owner.pk)
    else:
        owner_name = ""
        owner_id = None

    return {
        "id": appt.id,
        "patient_name": appt.patient.name,
        "owner_name": owner_name,
        "owner_id": owner_id,
        "pet_id": appt.patient.id,
        "vet_id": vet_id,
        "vet_name": vet_name,
        "date": date,
        "time": time_val,
        "reason": appt.reason_for_visit,
        "status": appt.status,
    }


def _appointment_queryset():
    """Base queryset with all the select_related joins we always need."""
    return Appointment.objects.select_related(
        "slot",
        "slot__schedule",
        "slot__schedule__vet",
        "slot__schedule__vet__clinical_staff",
        "slot__schedule__vet__clinical_staff__user",
        "patient",
        "patient__owner",
        "patient__owner__user",
    )


# ---------------------------------------------------------------------------
# 1. Vet Slots
# ---------------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([AllowAny])
def vet_slots(request, vet_id):
    """
    GET /api/v1/vets/{vet_id}/slots/
    Return free time-slots for a vet. Auto-creates schedules/slots for any days 
    in the next 180 days (6 months) that are missing, then returns all free slots in that range.
    """
    from apps.users.models import Veterinarian
    try:
        vet = Veterinarian.objects.get(pk=vet_id)
    except Veterinarian.DoesNotExist:
        return Response({"error": "Veterinarian not found"}, status=status.HTTP_404_NOT_FOUND)

    local_now = timezone.localtime(timezone.now())
    today = local_now.date()
    end_date = today + timedelta(days=180)

    # 1. Encontrar qué fechas en el rango [today, end_date] ya tienen agenda creada
    existing_schedules = VetSchedule.objects.filter(
        vet=vet,
        start_date__gte=today,
        start_date__lte=end_date
    ).values_list('start_date', flat=True)
    existing_dates = set(existing_schedules)

    # 2. Identificar fechas faltantes
    missing_dates = []
    for day_offset in range(181):  # 0 a 180 días inclusive
        day = today + timedelta(days=day_offset)
        if day not in existing_dates:
            missing_dates.append(day)

    # 3. Crear agendas y slots para las fechas faltantes de forma atómica y optimizada
    if missing_dates:
        from django.db import transaction
        with transaction.atomic():
            for day in missing_dates:
                schedule = VetSchedule.objects.create(vet=vet, start_date=day, end_date=day)
                hour, minute = 9, 0
                slots_to_create = []
                while hour < 17:
                    start = time(hour, minute)
                    end_minute = minute + 30
                    end_hour = hour
                    if end_minute >= 60:
                        end_minute -= 60
                        end_hour += 1
                    end = time(end_hour, end_minute)
                    slots_to_create.append(
                        TimeSlot(schedule=schedule, start_time=start, end_time=end, status="FREE")
                    )
                    minute += 30
                    if minute >= 60:
                        minute -= 60
                        hour += 1
                TimeSlot.objects.bulk_create(slots_to_create)

    # 4. Retornar todos los slots libres dentro del rango de 180 días
    slots = TimeSlot.objects.filter(
        schedule__vet_id=vet_id,
        status="FREE",
        schedule__start_date__gte=today,
        schedule__start_date__lte=end_date
    ).select_related("schedule")

    data = [
        {
            "id": s.id,
            "date": str(s.schedule.start_date),
            "start_time": str(s.start_time),
            "end_time": str(s.end_time),
            "status": s.status,
        }
        for s in slots
    ]
    return Response(data)


# ---------------------------------------------------------------------------
# 2. Schedule Calendar
# ---------------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([AllowAny])
def schedule_calendar(request):
    """
    GET /api/v1/schedules/calendar/
    Appointments grouped by date for the next 7 days.
    """
    today = timezone.now().date()
    end = today + timedelta(days=7)

    appointments = (
        _appointment_queryset()
        .filter(slot__schedule__start_date__gte=today, slot__schedule__start_date__lt=end)
        .exclude(status="CANCELLED")
        .order_by("slot__schedule__start_date", "slot__start_time")
    )

    grouped = {}
    for appt in appointments:
        d = str(appt.slot.schedule.start_date)
        if d not in grouped:
            grouped[d] = []
        grouped[d].append({
            "id": appt.id,
            "time": str(appt.slot.start_time),
            "patient_name": appt.patient.name,
            "vet_name": _vet_display_name(appt.slot.schedule.vet),
            "status": appt.status,
        })

    result = [{"date": d, "appointments": appts} for d, appts in sorted(grouped.items())]
    return Response(result)


# ---------------------------------------------------------------------------
# 3. Appointment List (GET & POST)
# ---------------------------------------------------------------------------

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def appointment_list(request):
    """
    GET  /api/v1/appointments/  → list all appointments
    POST /api/v1/appointments/  → create a new appointment
    """
    if request.method == "GET":
        appointments = _appointment_queryset().order_by("-id")
        data = [_serialize_appointment(a) for a in appointments]
        return Response(data)

    # POST
    slot_id = request.data.get("slot_id")
    patient_id = request.data.get("patient_id")
    reason = request.data.get("reason", "")

    if not slot_id or not patient_id:
        return Response(
            {"error": "slot_id and patient_id are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        slot = TimeSlot.objects.get(pk=slot_id)
    except TimeSlot.DoesNotExist:
        return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        patient = Patient.objects.get(pk=patient_id)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

    if slot.status != "FREE":
        return Response({"error": "Slot is not available"}, status=status.HTTP_400_BAD_REQUEST)

    # Validar fecha/hora en el pasado y límite de 6 meses
    from datetime import datetime
    local_now = timezone.localtime(timezone.now()).replace(tzinfo=None)
    appt_datetime = datetime.combine(slot.schedule.start_date, slot.start_time)

    if appt_datetime < local_now:
        return Response(
            {"error": "No se pueden agendar citas para fechas u horarios en el pasado."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if slot.schedule.start_date > local_now.date() + timedelta(days=180):
        return Response(
            {"error": "No se pueden agendar citas a más de 6 meses de anticipación."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    appt = Appointment.objects.create(
        slot=slot, patient=patient, reason_for_visit=reason, status="SCHEDULED"
    )
    slot.status = "BOOKED"
    slot.save()

    # Re-fetch with joins for serialization
    appt = _appointment_queryset().get(pk=appt.pk)
    return Response(_serialize_appointment(appt), status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# 4. Cancel Appointment
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def appointment_cancel(request, id):
    """POST /api/v1/appointments/{id}/cancel/"""
    try:
        appt = Appointment.objects.select_related("slot__schedule").get(pk=id)
    except Appointment.DoesNotExist:
        return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

    # 1. Validar por estado
    if appt.status in ['CHECKED_IN', 'COMPLETED']:
        return Response({"error": "No se puede cancelar una cita que ya está en atención o completada."}, status=status.HTTP_400_BAD_REQUEST)
    if appt.status == 'CANCELLED':
        return Response({"error": "La cita ya está cancelada."}, status=status.HTTP_400_BAD_REQUEST)

    # 2. Validar si ya pasó o está en la hora programada
    if appt.slot:
        from datetime import datetime
        appt_datetime = datetime.combine(appt.slot.schedule.start_date, appt.slot.start_time)
        
        current_time = timezone.now()
        if timezone.is_aware(current_time):
            local_now = timezone.localtime(current_time).replace(tzinfo=None)
        else:
            local_now = current_time
            
        if appt_datetime <= local_now:
            return Response({"error": "No se puede cancelar una cita que ya ha comenzado o cuyo horario ya pasó."}, status=status.HTTP_400_BAD_REQUEST)

    appt.status = "CANCELLED"
    appt.save()

    if appt.slot:
        appt.slot.status = "FREE"
        appt.slot.save()

    return Response({"message": "Appointment cancelled successfully"})


# ---------------------------------------------------------------------------
# 5. Confirm Appointment
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def appointment_confirm(request, id):
    """POST /api/v1/appointments/{id}/confirm/"""
    try:
        appt = Appointment.objects.get(pk=id)
    except Appointment.DoesNotExist:
        return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

    appt.status = "CONFIRMED"
    appt.save()
    return Response({"message": "Appointment confirmed successfully"})


# ---------------------------------------------------------------------------
# 6. Check-In Appointment
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def appointment_check_in(request, id):
    """POST /api/v1/appointments/{id}/check-in/"""
    try:
        appt = Appointment.objects.select_related("patient").get(pk=id)
    except Appointment.DoesNotExist:
        return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

    # Guard: prevent duplicate check-in
    if appt.status == "CHECKED_IN":
        return Response(
            {"error": "Esta cita ya fue registrada en sala de espera."},
            status=status.HTTP_409_CONFLICT,
        )
    if appt.status == "COMPLETED":
        return Response(
            {"error": "No se puede hacer check-in de una cita ya completada."},
            status=status.HTTP_409_CONFLICT,
        )
    if appt.status == "CANCELLED":
        return Response(
            {"error": "No se puede hacer check-in de una cita cancelada."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    appt.status = "CHECKED_IN"
    appt.checked_in_at = timezone.now()
    appt.save()

    priority = request.data.get("priority_level", "MEDIUM")
    WaitingListEntry.objects.create(
        patient=appt.patient,
        appointment=appt,
        priority_level=priority,
        status="WAITING",
    )

    return Response({"message": "Patient checked in successfully"})


# ---------------------------------------------------------------------------
# 7. Appointments Today
# ---------------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([AllowAny])
def appointments_today(request):
    """GET /api/v1/appointments/today/"""
    today = timezone.now().date()
    appointments = (
        _appointment_queryset()
        .filter(
            Q(slot__schedule__start_date=today) | Q(checked_in_at__date=today)
        )
        .order_by("slot__start_time")
    )
    data = [_serialize_appointment(a) for a in appointments]
    return Response(data)


# ---------------------------------------------------------------------------
# 8. Appointments Today by Vet
# ---------------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([AllowAny])
def appointments_today_by_vet(request, vet_id):
    """GET /api/v1/appointments/today/by-vet/{vet_id}/"""
    today = timezone.now().date()
    appointments = (
        _appointment_queryset()
        .filter(
            Q(slot__schedule__start_date=today) | Q(checked_in_at__date=today),
            slot__schedule__vet_id=vet_id,
        )
        .order_by("slot__start_time")
    )
    data = [_serialize_appointment(a) for a in appointments]
    return Response(data)


# ---------------------------------------------------------------------------
# 9. Waiting List
# ---------------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([AllowAny])
def waiting_list(request):
    """GET /api/v1/waiting-list/"""
    entries = WaitingListEntry.objects.filter(
        status__in=["WAITING", "ATTENDING"]
    ).select_related(
        "patient",
        "appointment",
        "patient__owner",
        "patient__owner__user",
    ).order_by("id")

    data = []
    for entry in entries:
        owner = entry.patient.owner
        if owner:
            owner_user = owner.user
            owner_name = f"{owner_user.first_name} {owner_user.last_name}".strip() or owner_user.email
        else:
            owner_name = ""

        data.append({
            "id": entry.id,
            "patient_name": entry.patient.name,
            "owner_name": owner_name,
            "owner_id": str(owner.pk) if owner else None,
            "appointment_id": entry.appointment_id,
            "priority": entry.priority_level,
            "status": entry.status,
            "checked_in_at": (
                entry.appointment.checked_in_at.isoformat()
                if entry.appointment and entry.appointment.checked_in_at
                else None
            ),
        })
    return Response(data)


# ---------------------------------------------------------------------------
# 10. Waiting List – Call Next
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def waiting_list_call_next(request, id):
    """POST /api/v1/waiting-list/{id}/call-next/"""
    try:
        entry = WaitingListEntry.objects.select_related("appointment").get(pk=id)
    except WaitingListEntry.DoesNotExist:
        return Response({"error": "Waiting list entry not found"}, status=status.HTTP_404_NOT_FOUND)

    entry.status = "ATTENDING"
    entry.save()

    if entry.appointment:
        entry.appointment.status = "COMPLETED"
        entry.appointment.save()

    return Response({"message": "Patient called successfully"})


# ---------------------------------------------------------------------------
# 11. Appointment Consultations
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def appointment_consultations(request, id):
    """POST /api/v1/appointments/{id}/consultations/"""
    try:
        appt = Appointment.objects.select_related("patient").get(pk=id)
    except Appointment.DoesNotExist:
        return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

    consultation_data = {
        "date": str(timezone.now().date()),
        "diagnosis": request.data.get("diagnosis", ""),
        "treatment": request.data.get("treatment", ""),
        "symptoms": request.data.get("symptoms", ""),
        "weight": request.data.get("weight", ""),
        "temperature": request.data.get("temperature", ""),
        "prescriptions": request.data.get("prescriptions", ""),
        "notes": request.data.get("notes", ""),
        "follow_up_date": request.data.get("follow_up_date", ""),
    }

    # Get or create clinical records for the patient
    record, _ = ClinicalRecords.objects.get_or_create(
        patient=appt.patient,
        defaults={
            "opened_at": timezone.now().date(),
            "allergies_history": "",
            "medical_alerts": "[]",
        },
    )

    # Append consultation to medical_alerts as JSON array
    try:
        existing = json.loads(record.medical_alerts) if record.medical_alerts else []
    except (json.JSONDecodeError, TypeError):
        existing = []
    if not isinstance(existing, list):
        existing = [existing] if existing else []

    existing.append(consultation_data)
    record.medical_alerts = json.dumps(existing, ensure_ascii=False)
    record.save()

    # Mark appointment as completed
    appt.status = "COMPLETED"
    appt.save()

    return Response(consultation_data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# 12. Consultation Supplies Used (stub – stock module handles it)
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def consultation_supplies_used(request, id):
    """POST /api/v1/consultations/{id}/supplies-used/"""
    return Response({"message": "Supplies recorded successfully"})
