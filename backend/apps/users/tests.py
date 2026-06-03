from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import NaturalPerson, AuditLog
from apps.owners.models import Owner

User = get_user_model()

class UsersAuthTestCase(APITestCase):
    def setUp(self):
        # Crear grupos requeridos por el sistema
        self.owner_group, _ = Group.objects.get_or_create(name='owner')
        self.receptionist_group, _ = Group.objects.get_or_create(name='receptionist')
        self.vet_group, _ = Group.objects.get_or_create(name='veterinarian')
        self.manager_group, _ = Group.objects.get_or_create(name='manager')

        # Crear usuarios para pruebas de login y permisos
        self.test_password = 'Password123!'
        
        self.receptionist_user = User.objects.create_user(
            email='recep@petcare.com',
            password=self.test_password,
            first_name='Ana',
            last_name='Gomez',
            is_active=True
        )
        self.receptionist_user.groups.add(self.receptionist_group)

        self.vet_user = User.objects.create_user(
            email='vet_test@petcare.com',
            password=self.test_password,
            first_name='Luis',
            last_name='Paz',
            is_active=True
        )
        self.vet_user.groups.add(self.vet_group)

    def test_owner_registration_success(self):
        payload = {
            'email': 'new_owner@test.com',
            'password': 'SecurePassword123!',
            'first_name': 'Carlos',
            'last_name': 'Mendoza',
            'phone': '+541155554444',
            'address': 'Av. Libertador 1420',
            'dni': '35123456',
            'location': 'Sede Palermo',
            'emergency_contact': '+541155559999'
        }
        
        response = self.client.post('/api/v1/auth/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], 'new_owner@test.com')

        # Verificar creación en Base de Datos
        user_exists = User.objects.filter(email='new_owner@test.com').exists()
        self.assertTrue(user_exists)
        
        user = User.objects.get(email='new_owner@test.com')
        self.assertTrue(user.groups.filter(name='owner').exists())
        
        # Verificar creación de modelos hijos
        self.assertTrue(NaturalPerson.objects.filter(user=user).exists())
        self.assertTrue(Owner.objects.filter(user=user).exists())

    def test_registration_invalid_phone(self):
        payload = {
            'email': 'invalid_phone@test.com',
            'password': 'SecurePassword123!',
            'first_name': 'Carlos',
            'last_name': 'Mendoza',
            'phone': 'DFHSJD',
            'address': 'Av. Libertador 1420',
            'dni': '35123456'
        }
        response = self.client.post('/api/v1/auth/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('El teléfono debe tener un formato válido', response.data['error'])

    def test_registration_missing_fields(self):
        payload = {
            'email': 'incomplete@test.com',
            # Falta contraseña
            'first_name': 'Test'
        }
        response = self.client.post('/api/v1/auth/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_registration_duplicate_email(self):
        # Registrar primero
        payload = {
            'email': 'dup@test.com',
            'password': 'Password123!',
            'first_name': 'Test'
        }
        self.client.post('/api/v1/auth/register/', payload, format='json')
        
        # Intentar registrar de nuevo con mismo email
        response = self.client.post('/api/v1/auth/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_login_success(self):
        payload = {
            'email': self.receptionist_user.email,
            'password': self.test_password
        }
        response = self.client.post('/api/v1/auth/login/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], self.receptionist_user.email)

    def test_login_invalid_credentials(self):
        payload = {
            'email': self.receptionist_user.email,
            'password': 'WrongPassword!'
        }
        response = self.client.post('/api/v1/auth/login/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_veterinarian_success(self):
        # El endpoint login_veterinarian usa username y password en request.data
        payload = {
            'username': self.vet_user.email,
            'password': self.test_password
        }
        response = self.client.post('/api/v1/auth/login-veterinarian/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mensaje', response.data)

    def test_login_veterinarian_denied_role(self):
        # Un recepcionista intentando ingresar a la ruta de veterinarios
        payload = {
            'username': self.receptionist_user.email,
            'password': self.test_password
        }
        response = self.client.post('/api/v1/auth/login-veterinarian/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_verify_user_authenticated(self):
        self.client.force_authenticate(user=self.receptionist_user)
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.receptionist_user.email)

    def test_verify_user_unauthenticated(self):
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
