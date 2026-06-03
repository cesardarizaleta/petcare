import json
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import ClinicalStaff, Veterinarian, NaturalPerson
from apps.owners.models import Owner
from apps.patients.models import Patient, ClinicalRecords, VaccinationPlan, VaccinationDewormingEvent

User = get_user_model()

class PatientsTestCase(APITestCase):
    def setUp(self):
        # 1. Crear grupos
        self.owner_group, _ = Group.objects.get_or_create(name='owner')

        # 2. Crear Propietario
        self.owner_user = User.objects.create_user(
            email='owner_pet_test@petcare.com',
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

        # 4. Crear expediente clínico base
        self.record = ClinicalRecords.objects.create(
            patient=self.patient,
            opened_at=timezone.now().date(),
            allergies_history='Penicilina',
            medical_alerts=json.dumps([
                {
                    "date": "2026-05-30",
                    "diagnosis": "Gastroenteritis",
                    "treatment": "Dieta líquida",
                    "symptoms": "Vómitos",
                    "weight": "10.2",
                    "temperature": "39.1",
                    "prescriptions": "Probióticos",
                    "notes": "Evolución favorable"
                }
            ])
        )

    def test_patient_list_api(self):
        response = self.client.get('/api/v1/pets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # La respuesta es una lista paginada o directa dependendiendo del setup, pero debe traer a Firu
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['name'], 'Firu')

    def test_patient_detail_and_update(self):
        # GET Detail
        response = self.client.get(f'/api/v1/pets/{self.patient.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Firu')

        # PATCH Update
        payload = {
            'name': 'Firu Modificado',
            'weight_kg': 11.2
        }
        patch_response = self.client.patch(f'/api/v1/pets/{self.patient.id}/', payload, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['name'], 'Firu Modificado')
        
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.name, 'Firu Modificado')

    def test_pet_medical_record_summary(self):
        response = self.client.get(f'/api/v1/pets/{self.patient.id}/medical-record/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['patient_name'], 'Firu')
        self.assertEqual(response.data['allergies'], 'Penicilina')
        self.assertTrue(len(response.data['consultations']) > 0)
        self.assertEqual(response.data['consultations'][0]['diagnosis'], 'Gastroenteritis')

    def test_pet_medical_record_full(self):
        response = self.client.get(f'/api/v1/pets/{self.patient.id}/medical-record/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['patient_name'], 'Firu')
        self.assertEqual(response.data['allergies'], 'Penicilina')
        self.assertEqual(response.data['owner']['email'], self.owner_user.email)

    def test_vaccination_schedule_and_register_event(self):
        # 1. Registrar evento de vacunación
        event_payload = {
            'event_type': 'VACCINE',
            'dose': '1ml',
            'applied_date': '2026-05-31',
            'sanitary_batch': 'LOTE-VAC-999',
            'next_due_date': '2027-05-31',
            'vaccine_name': 'Quíntuple'
        }
        
        post_response = self.client.post(f'/api/v1/pets/{self.patient.id}/vaccination-events/', event_payload, format='json')
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(post_response.data['event_type'], 'VACCINE')
        self.assertEqual(post_response.data['lot'], 'LOTE-VAC-999')
        self.assertEqual(post_response.data['vaccine_name'], 'Quíntuple')

        # Verificar BD
        event_obj = VaccinationDewormingEvent.objects.get(sanitary_batch='LOTE-VAC-999')
        self.assertEqual(event_obj.vaccine_name, 'Quíntuple')

        # 2. Consultar Cronograma/Schedule
        get_response = self.client.get(f'/api/v1/pets/{self.patient.id}/vaccination-plan/schedule/')
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data), 1)
        self.assertEqual(get_response.data[0]['lot'], 'LOTE-VAC-999')
        self.assertEqual(get_response.data[0]['vaccine_name'], 'Quíntuple')

    def test_vaccination_event_future_applied_date(self):
        # Intentar registrar una vacuna aplicada en el futuro
        tomorrow = (timezone.now() + timedelta(days=1)).date()
        event_payload = {
            'event_type': 'VACCINE',
            'dose': '1ml',
            'applied_date': str(tomorrow),
            'vaccine_name': 'Quíntuple'
        }
        response = self.client.post(f'/api/v1/pets/{self.patient.id}/vaccination-events/', event_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('La fecha de aplicación no puede ser una fecha futura', response.data['error'])

    def test_vaccination_event_past_next_due_date(self):
        # Intentar registrar con una fecha de seguimiento anterior a la fecha de aplicación
        event_payload = {
            'event_type': 'VACCINE',
            'dose': '1ml',
            'applied_date': '2026-05-31',
            'next_due_date': '2026-05-30',  # Siguiente fecha antes que la de aplicación
            'vaccine_name': 'Quíntuple'
        }
        response = self.client.post(f'/api/v1/pets/{self.patient.id}/vaccination-events/', event_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('La próxima fecha debe ser posterior a la fecha de aplicación', response.data['error'])
