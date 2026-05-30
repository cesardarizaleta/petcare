#!/usr/bin/env python
import os
import sys
from pathlib import Path
import django
from datetime import date, timedelta

# Set up Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import NaturalPerson, ClinicalStaff, Veterinarian
from apps.owners.models import Owner
from apps.stock.models import Supply, Supplier

User = get_user_model()

def seed_data():
    print("Iniciando la siembra de datos de prueba en la base de datos principal...")

    # 1. Crear grupos
    owner_group, _ = Group.objects.get_or_create(name='owner')
    receptionist_group, _ = Group.objects.get_or_create(name='receptionist')
    veterinarian_group, _ = Group.objects.get_or_create(name='veterinarian')
    manager_group, _ = Group.objects.get_or_create(name='manager')
    tech_group, _ = Group.objects.get_or_create(name='technician')
    vet_tech_group, _ = Group.objects.get_or_create(name='veterinary_technician')
    print("Grupos de seguridad creados/verificados con éxito.")


    # 2. Crear usuario Propietario (Owner)
    owner_email = 'propietario@petcare.com'
    owner_user, created = User.objects.get_or_create(
        email=owner_email,
        defaults={
            'username': 'carlos_mendoza',
            'first_name': 'Carlos',
            'last_name': 'Mendoza',
            'is_active': True
        }
    )
    if created:
        owner_user.set_password('petcare123')
        owner_user.save()
    owner_user.groups.add(owner_group)

    owner_np, _ = NaturalPerson.objects.get_or_create(
        user=owner_user,
        defaults={
            'phone': '+541155554444',
            'address': 'Av. Libertador 1420, CABA',
            'dni': '35123456'
        }
    )

    owner_profile, _ = Owner.objects.get_or_create(
        user=owner_user,
        defaults={
            'natural_person': owner_np,
            'location': 'Sede Palermo',
            'emergency_contact': '+541155559999'
        }
    )
    
    # 3. Crear usuario Recepcionista
    receptionist_email = 'recepcion@petcare.com'
    receptionist_user, created = User.objects.get_or_create(
        email=receptionist_email,
        defaults={
            'username': 'ana_gomez',
            'first_name': 'Ana',
            'last_name': 'Gomez',
            'is_active': True
        }
    )
    if created:
        receptionist_user.set_password('petcare123')
        receptionist_user.save()
    receptionist_user.groups.add(receptionist_group)

    receptionist_np, _ = NaturalPerson.objects.get_or_create(
        user=receptionist_user,
        defaults={
            'phone': '+541155552222',
            'address': 'Sede Centro',
            'dni': '28456123'
        }
    )

    # 4. Crear usuario Veterinario
    vet_email = 'vet@petcare.com'
    vet_user, created = User.objects.get_or_create(
        email=vet_email,
        defaults={
            'username': 'luis_paz',
            'first_name': 'Dr. Luis',
            'last_name': 'Paz',
            'is_active': True
        }
    )
    if created:
        vet_user.set_password('petcare123')
        vet_user.save()
    vet_user.groups.add(veterinarian_group)

    vet_np, _ = NaturalPerson.objects.get_or_create(
        user=vet_user,
        defaults={
            'phone': '+541155553333',
            'address': 'Sede Palermo',
            'dni': '30123789'
        }
    )

    clinical_staff, _ = ClinicalStaff.objects.get_or_create(
        user=vet_user,
        defaults={'natural_person': vet_np}
    )

    veterinarian, _ = Veterinarian.objects.get_or_create(
        clinical_staff=clinical_staff,
        defaults={'specialty': 'Cirugía General'}
    )

    # 4.1. Crear usuario Gerente
    manager_email = 'admin@petcare.com'
    manager_user, created = User.objects.get_or_create(
        email=manager_email,
        defaults={
            'username': 'admin_gerente',
            'first_name': 'Admin',
            'last_name': 'Gerente',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        manager_user.set_password('petcare123')
        manager_user.save()
    manager_user.groups.add(manager_group)

    # 4.2. Crear usuario Técnico de Inventario
    tech_email = 'tecnico@petcare.com'
    tech_user, created = User.objects.get_or_create(
        email=tech_email,
        defaults={
            'username': 'tecnico_inventario',
            'first_name': 'Técnico',
            'last_name': 'Inventario',
            'is_active': True
        }
    )
    if created:
        tech_user.set_password('petcare123')
        tech_user.save()
    tech_user.groups.add(tech_group, vet_tech_group)


    # 5. Crear datos de Stock (Insumos y Proveedor)
    supplier, _ = Supplier.objects.get_or_create(
        name='Farmacia Veterinaria Central',
        defaults={
            'phone': '0800-555-8387',
            'email': 'ventas@farmaciavet.com',
            'address': 'Industrial Park Sector B'
        }
    )

    # Insumo con stock crítico
    supply_critical, _ = Supply.objects.get_or_create(
        sku='MED-AMOX-500',
        defaults={
            'name': 'Amoxicilina 500mg',
            'category': 'MEDICINE',
            'min_stock': 50
        }
    )
    # Insumo con stock saludable
    supply_healthy, _ = Supply.objects.get_or_create(
        sku='CON-GUA-LIT',
        defaults={
            'name': 'Guantes de Látex',
            'category': 'CONSUMABLE',
            'min_stock': 100
        }
    )

    print("Semilla de base de datos completada con éxito.")
    print("------------------------------------------------------------------")
    print("TOKENS JWT DE PRUEBA GENERADOS:")
    
    owner_token = RefreshToken.for_user(owner_user).access_token
    receptionist_token = RefreshToken.for_user(receptionist_user).access_token
    vet_token = RefreshToken.for_user(vet_user).access_token

    print(f"PROPIETARIO (Carlos Mendoza) - Email: {owner_email}")
    print(f"TOKEN: {owner_token}")
    print("------------------------------------------------------------------")
    print(f"RECEPCIONISTA (Ana Gomez) - Email: {receptionist_email}")
    print(f"TOKEN: {receptionist_token}")
    print("------------------------------------------------------------------")
    print(f"VETERINARIO (Dr. Luis Paz) - Email: {vet_email}")
    print(f"TOKEN: {vet_token}")
    print("------------------------------------------------------------------")

if __name__ == '__main__':
    seed_data()
