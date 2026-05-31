import json
from datetime import date, time, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import ClinicalStaff, Veterinarian, NaturalPerson
from apps.owners.models import Owner
from apps.patients.models import Patient
from apps.appointments.models import VetSchedule, TimeSlot, Appointment, WaitingListEntry

User = get_user_model()

class AppointmentsTestCase(APITestCase):
    def setUp(self):
        # 1. Crear grupos
        self.owner_group, _ = Group.objects.get_or_create(name='owner')
        self.vet_group, _ = Group.objects.get_or_create(name='veterinarian')

        # 2. Crear Propietario
        self.owner_user = User.objects.create_user(
            email='owner_test@petcare.com',
            password='Password123!',
            first_name='Carlos',
            last_name='Mendoza',
            is_active=True
        )
        self.owner_user.groups.add(self.owner_group)
        self.owner_np = NaturalPerson.objects.create(user=self.owner_user, phone='1234', address='Av 123', dni='DNI123')
        self.owner_profile = Owner.objects.create(user=self.owner_user, natural_person=self.owner_np)

        # 3. Crear Paciente (Mascota)
        self.patient = Patient.objects.create(
            name='Firu',
            species_breed='Dog - Pug',
            gender='Macho',
            birth_date=date(2020, 1, 1),
            current_weight=10.5,
            owner=self.owner_profile,
            physical_marks='None',
            microchip_id='CHIP123',
            reproductive_status='Castrado'
        )

        # 4. Crear Veterinario
        self.vet_user = User.objects.create_user(
            email='vet_test@petcare.com',
            password='Password123!',
            first_name='Dr. Luis',
            last_name='Paz',
            is_active=True
        )
        self.vet_user.groups.add(self.vet_group)
        self.vet_np = NaturalPerson.objects.create(user=self.vet_user, phone='5678', address='Av 456', dni='DNI456')
        self.vet_staff = ClinicalStaff.objects.create(user=self.vet_user, natural_person=self.vet_np)
        self.vet_profile = Veterinarian.objects.create(clinical_staff=self.vet_staff, specialty='Cirugía')

        # 5. Crear Schedule y Slot de prueba
        tomorrow = timezone.now().date() + timedelta(days=1)
        self.schedule = VetSchedule.objects.create(
            vet=self.vet_profile,
            start_date=tomorrow,
            end_date=tomorrow
        )
        self.slot = TimeSlot.objects.create(
            schedule=self.schedule,
            start_time=time(10, 0),
            end_time=time(10, 30),
            status='FREE'
        )

    def test_vet_slots_retrieval_and_autocreate(self):
        # Si consultamos un veterinario que no tiene slots en absoluto, debe autogenerar
        new_vet_user = User.objects.create_user(
            email='new_vet@petcare.com',
            password='Password123!',
            first_name='Doc',
            last_name='New',
            is_active=True
        )
        new_vet_user.groups.add(self.vet_group)
        new_vet_np = NaturalPerson.objects.create(user=new_vet_user, phone='111', address='111', dni='111')
        new_vet_staff = ClinicalStaff.objects.create(user=new_vet_user, natural_person=new_vet_np)
        new_vet_profile = Veterinarian.objects.create(clinical_staff=new_vet_staff, specialty='Dentista')

        # Get slots
        response = self.client.get(f'/api/v1/vets/{new_vet_profile.id}/slots/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debe autogenerar slots (hoy + 5 días = 6 días, 9:00 a 17:00 en bloques de 30 mins)
        self.assertTrue(len(response.data) > 0)

    def test_schedule_calendar(self):
        # Primero crear una cita
        Appointment.objects.create(
            slot=self.slot,
            patient=self.patient,
            reason_for_visit='Control',
            status='SCHEDULED'
        )
        self.slot.status = 'BOOKED'
        self.slot.save()

        response = self.client.get('/api/v1/schedules/calendar/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_appointment_booking_and_cancellation_flow(self):
        self.client.force_authenticate(user=self.owner_user)

        # 1. Agendar cita
        payload = {
            'slot_id': self.slot.id,
            'patient_id': self.patient.id,
            'reason': 'Consulta general de rutina'
        }
        response = self.client.post('/api/v1/appointments/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'SCHEDULED')
        self.assertEqual(response.data['reason'], 'Consulta general de rutina')

        appt_id = response.data['id']
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.status, 'BOOKED')

        # 2. Confirmar cita
        confirm_resp = self.client.post(f'/api/v1/appointments/{appt_id}/confirm/')
        self.assertEqual(confirm_resp.status_code, status.HTTP_200_OK)
        
        appt = Appointment.objects.get(pk=appt_id)
        self.assertEqual(appt.status, 'CONFIRMED')

        # 3. Cancelar cita
        cancel_resp = self.client.post(f'/api/v1/appointments/{appt_id}/cancel/')
        self.assertEqual(cancel_resp.status_code, status.HTTP_200_OK)

        appt.refresh_from_db()
        self.assertEqual(appt.status, 'CANCELLED')
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.status, 'FREE')

    def test_check_in_and_waiting_list(self):
        appt = Appointment.objects.create(
            slot=self.slot,
            patient=self.patient,
            reason_for_visit='Fiebre',
            status='SCHEDULED'
        )
        self.slot.status = 'BOOKED'
        self.slot.save()

        # Check-in
        checkin_payload = {'priority_level': 'HIGH'}
        response = self.client.post(f'/api/v1/appointments/{appt.id}/check-in/', checkin_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        appt.refresh_from_db()
        self.assertEqual(appt.status, 'CHECKED_IN')
        self.assertIsNotNone(appt.checked_in_at)

        # Verificar lista de espera
        waiting_entries = WaitingListEntry.objects.filter(appointment=appt)
        self.assertTrue(waiting_entries.exists())
        entry = waiting_entries.first()
        self.assertEqual(entry.priority_level, 'HIGH')
        self.assertEqual(entry.status, 'WAITING')

        # List waiting list
        wl_resp = self.client.get('/api/v1/waiting-list/')
        self.assertEqual(wl_resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any(e['id'] == entry.id for e in wl_resp.data))

        # Call next
        call_resp = self.client.post(f'/api/v1/waiting-list/{entry.id}/call-next/')
        self.assertEqual(call_resp.status_code, status.HTTP_200_OK)

        entry.refresh_from_db()
        self.assertEqual(entry.status, 'ATTENDING')
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'COMPLETED')

    def test_appointment_consultation_creation(self):
        appt = Appointment.objects.create(
            slot=self.slot,
            patient=self.patient,
            reason_for_visit='Vacunas',
            status='SCHEDULED'
        )
        self.slot.status = 'BOOKED'
        self.slot.save()

        consult_payload = {
            'diagnosis': 'Sano',
            'treatment': 'Ninguno',
            'symptoms': 'Ninguno',
            'weight': '10.5',
            'temperature': '38.5',
            'prescriptions': 'Ninguna',
            'notes': 'Paciente en excelente estado'
        }
        
        response = self.client.post(f'/api/v1/appointments/{appt.id}/consultations/', consult_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['diagnosis'], 'Sano')

        appt.refresh_from_db()
        self.assertEqual(appt.status, 'COMPLETED')
