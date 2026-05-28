import json

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, generics

from apps.owners.serializers import PetSerializer
from .models import Patient, ClinicalRecords, VaccinationPlan, VaccinationDewormingEvent


# ---------------------------------------------------------------------------
# 1. Medical Record Summary
# ---------------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([AllowAny])
def pet_medical_record_summary(request, pet_id):
    """
    GET /api/v1/pets/{pet_id}/medical-record/summary/
    Quick summary: allergies, medical alerts, basic patient info.
    """
    try:
        patient = Patient.objects.select_related("owner", "owner__user").get(pk=pet_id)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

    record, _ = ClinicalRecords.objects.get_or_create(
        patient=patient,
        defaults={
            "opened_at": timezone.now().date(),
            "allergies_history": "",
            "medical_alerts": "[]",
        },
    )

    # Parse consultations stored in medical_alerts
    try:
        consultations = json.loads(record.medical_alerts) if record.medical_alerts else []
    except (json.JSONDecodeError, TypeError):
        consultations = []
    if not isinstance(consultations, list):
        consultations = []

    return Response({
        "patient_name": patient.name,
        "species_breed": patient.species_breed,
        "weight": patient.current_weight,
        "allergies": record.allergies_history,
        "medical_alerts": record.medical_alerts,
        "consultations": consultations,
    })


# ---------------------------------------------------------------------------
# 2. Full Medical Record
# ---------------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([AllowAny])
def pet_medical_record(request, pet_id):
    """
    GET /api/v1/pets/{pet_id}/medical-record/
    Full record including owner info and vaccination events.
    """
    try:
        patient = Patient.objects.select_related("owner", "owner__user").get(pk=pet_id)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

    record, _ = ClinicalRecords.objects.get_or_create(
        patient=patient,
        defaults={
            "opened_at": timezone.now().date(),
            "allergies_history": "",
            "medical_alerts": "[]",
        },
    )

    # Parse consultations stored in medical_alerts
    try:
        consultations = json.loads(record.medical_alerts) if record.medical_alerts else []
    except (json.JSONDecodeError, TypeError):
        consultations = []
    if not isinstance(consultations, list):
        consultations = []

    # Owner info
    owner = patient.owner
    if owner:
        owner_user = owner.user
        owner_info = {
            "id": str(owner_user.id),
            "name": f"{owner_user.first_name} {owner_user.last_name}".strip() or owner_user.email,
            "email": owner_user.email,
        }
    else:
        owner_info = None

    # Vaccination events
    events = VaccinationDewormingEvent.objects.filter(
        plan__patient=patient
    ).order_by("-applied_date")

    vaccination_events = [
        {
            "id": e.id,
            "event_type": e.event_type,
            "vaccine_name": e.event_type,
            "dose": e.dose,
            "applied_date": str(e.applied_date),
            "next_due_date": str(e.next_due_date) if e.next_due_date else None,
            "lot": e.sanitary_batch,
        }
        for e in events
    ]

    return Response({
        "patient_name": patient.name,
        "species_breed": patient.species_breed,
        "gender": patient.gender,
        "birth_date": str(patient.birth_date),
        "weight": patient.current_weight,
        "microchip_id": patient.microchip_id,
        "reproductive_status": patient.reproductive_status,
        "physical_marks": patient.physical_marks,
        "owner": owner_info,
        "allergies": record.allergies_history,
        "medical_alerts": record.medical_alerts,
        "consultations": consultations,
        "vaccination_events": vaccination_events,
    })


# ---------------------------------------------------------------------------
# 3. Vaccination Schedule
# ---------------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([AllowAny])
def pet_vaccination_schedule(request, pet_id):
    """
    GET /api/v1/pets/{pet_id}/vaccination-plan/schedule/
    Vaccination & deworming events for a patient, ordered by most recent first.
    """
    events = VaccinationDewormingEvent.objects.filter(
        plan__patient_id=pet_id
    ).order_by("-applied_date")

    data = [
        {
            "id": e.id,
            "vaccine_name": e.event_type,
            "applied_date": str(e.applied_date),
            "next_due_date": str(e.next_due_date) if e.next_due_date else None,
            "dose": e.dose,
            "lot": e.sanitary_batch,
            "event_type": e.event_type,
        }
        for e in events
    ]
    return Response(data)


# ---------------------------------------------------------------------------
# 4. Register Vaccination Event
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def pet_vaccination_events(request, pet_id):
    """
    POST /api/v1/pets/{pet_id}/vaccination-events/
    Record a vaccine or deworming event for the patient.
    """
    try:
        patient = Patient.objects.get(pk=pet_id)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

    # Get or create an active vaccination plan for the patient
    plan, _ = VaccinationPlan.objects.get_or_create(
        patient=patient,
        is_active=True,
        defaults={"vet": None},
    )

    applied_date = request.data.get("applied_date")
    if not applied_date or applied_date == "":
        applied_date = timezone.now().date()

    next_due_date = request.data.get("next_due_date")
    if not next_due_date or next_due_date == "":
        next_due_date = None

    event = VaccinationDewormingEvent.objects.create(
        plan=plan,
        event_type=request.data.get("event_type", "VACCINE"),
        dose=request.data.get("dose", ""),
        applied_date=applied_date,
        sanitary_batch=request.data.get("sanitary_batch", ""),
        next_due_date=next_due_date,
    )

    return Response(
        {
            "id": event.id,
            "event_type": event.event_type,
            "vaccine_name": request.data.get("vaccine_name", event.event_type),
            "dose": event.dose,
            "applied_date": str(event.applied_date),
            "next_due_date": str(event.next_due_date) if event.next_due_date else None,
            "lot": event.sanitary_batch,
        },
        status=status.HTTP_201_CREATED,
    )


# ---------------------------------------------------------------------------
# 5. Patient List & Detail Views
# ---------------------------------------------------------------------------

class PatientListAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PetSerializer
    permission_classes = [AllowAny]


class PatientDetailUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PetSerializer
    permission_classes = [AllowAny]

