from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status
from apps.owners.models import Owner
from apps.users.models import NaturalPerson
from apps.patients.models import Patient, ClinicalRecords

User = get_user_model()

class OwnerAppTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Groups
        self.owner_group, _ = Group.objects.get_or_create(name='owner')
        self.receptionist_group, _ = Group.objects.get_or_create(name='receptionist')

        # Create Owner User
        self.owner_user = User.objects.create_user(
            email='owner@test.com',
            password='password123',
            first_name='Juan',
            last_name='Perez'
        )
        self.owner_user.groups.add(self.owner_group)

        # Create NaturalPerson data
        self.natural_person = NaturalPerson.objects.create(
            user=self.owner_user,
            phone='+123456789',
            address='Calle Falsa 123',
            dni='DNI12345'
        )

        # Create Owner profile
        self.owner_profile = Owner.objects.create(
            user=self.owner_user,
            natural_person=self.natural_person,
            location='Main Location',
            emergency_contact='911'
        )

        # Create Receptionist User
        self.receptionist_user = User.objects.create_user(
            email='receptionist@test.com',
            password='password123',
            first_name='Maria',
            last_name='Gomez'
        )
        self.receptionist_user.groups.add(self.receptionist_group)

    def test_get_owner_me(self):
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get('/api/v1/owners/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone'], '+123456789')
        self.assertEqual(response.data['address'], 'Calle Falsa 123')
        self.assertEqual(response.data['user']['email'], 'owner@test.com')

    def test_patch_owner_me(self):
        self.client.force_authenticate(user=self.owner_user)
        payload = {
            'first_name': 'Juan Carlos',
            'phone': '+987654321',
            'address': 'Nueva Direccion 456'
        }
        response = self.client.patch('/api/v1/owners/me/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response
        self.assertEqual(response.data['phone'], '+987654321')
        self.assertEqual(response.data['address'], 'Nueva Direccion 456')
        self.assertEqual(response.data['user']['first_name'], 'Juan Carlos')

        # Verify DB updates
        self.owner_user.refresh_from_db()
        self.natural_person.refresh_from_db()
        self.assertEqual(self.owner_user.first_name, 'Juan Carlos')
        self.assertEqual(self.natural_person.phone, '+987654321')
        self.assertEqual(self.natural_person.address, 'Nueva Direccion 456')

    def test_patch_owner_me_invalid_phone(self):
        self.client.force_authenticate(user=self.owner_user)
        payload = {
            'phone': 'DFHSJD'
        }
        response = self.client.patch('/api/v1/owners/me/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)

    def test_owner_me_pets_flow(self):
        self.client.force_authenticate(user=self.owner_user)
        
        # 1. GET initially empty
        response = self.client.get('/api/v1/owners/me/pets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # 2. POST register pet
        pet_payload = {
            'name': 'Firu',
            'species': 'Dog',
            'breed': 'Pug',
            'date_of_birth': '2022-05-15',
            'sex': 'M',
            'weight_kg': 8.5
        }
        response = self.client.post('/api/v1/owners/me/pets/', pet_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Firu')
        self.assertEqual(response.data['species'], 'Dog')
        self.assertEqual(response.data['breed'], 'Pug')
        self.assertEqual(response.data['sex'], 'M')
        self.assertEqual(response.data['weight_kg'], 8.5)

        # Verify in DB
        patient = Patient.objects.get(name='Firu')
        self.assertEqual(patient.species_breed, 'Dog - Pug')
        self.assertEqual(patient.gender, 'Macho')
        self.assertEqual(patient.owner, self.owner_profile)

        # Verify ClinicalRecords created
        self.assertTrue(ClinicalRecords.objects.filter(patient=patient).exists())

        # 3. GET listed
        response = self.client.get('/api/v1/owners/me/pets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Firu')

    def test_receptionist_views(self):
        # Authenticate as Receptionist
        self.client.force_authenticate(user=self.receptionist_user)

        # List owners
        response = self.client.get('/api/v1/owners/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user']['email'], 'owner@test.com')

        # Owner detail
        response = self.client.get(f'/api/v1/owners/{self.owner_profile.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'owner@test.com')

        # Owner update via PATCH
        payload = {
            'first_name': 'Juan Carlos',
            'phone': '+987654321',
        }
        response = self.client.patch(f'/api/v1/owners/{self.owner_profile.pk}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['first_name'], 'Juan Carlos')
        self.assertEqual(response.data['phone'], '+987654321')

    def test_permission_protection(self):
        # Authenticate as Owner trying to access Receptionist endpoints
        self.client.force_authenticate(user=self.owner_user)
        
        response = self.client.get('/api/v1/owners/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Authenticate as Receptionist trying to access Owner me endpoints
        self.client.force_authenticate(user=self.receptionist_user)
        response = self.client.get('/api/v1/owners/me/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
