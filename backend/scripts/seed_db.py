#!/usr/bin/env python
import os
import sys
from pathlib import Path
import django
from datetime import date, timedelta
from decimal import Decimal

# Set up Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from apps.users.models import NaturalPerson, ClinicalStaff, Veterinarian, AuditLog
from apps.owners.models import Owner
from apps.stock.models import Supply, SupplyBatch, Supplier, PurchaseOrder, PurchaseOrderItem
from apps.patients.models import Patient, ClinicalRecords, VaccinationPlan, VaccinationPlanItem, VaccinationDewormingEvent
from apps.appointments.models import VetSchedule, TimeSlot, Appointment, WaitingListEntry

User = get_user_model()

def seed_data():
    print("Iniciando la limpieza y siembra de datos...")
    
    # 1. Eliminar datos operativos antiguos
    print("Eliminando registros operativos antiguos...")
    WaitingListEntry.objects.all().delete()
    Appointment.objects.all().delete()
    TimeSlot.objects.all().delete()
    VetSchedule.objects.all().delete()
    VaccinationDewormingEvent.objects.all().delete()
    VaccinationPlanItem.objects.all().delete()
    VaccinationPlan.objects.all().delete()
    ClinicalRecords.objects.all().delete()
    Patient.objects.all().delete()
    PurchaseOrderItem.objects.all().delete()
    PurchaseOrder.objects.all().delete()
    SupplyBatch.objects.all().delete()
    Supply.objects.all().delete()
    Supplier.objects.all().delete()
    AuditLog.objects.all().delete()
    print("Tablas operativas limpiadas.")

    # 2. Asegurar que los grupos de seguridad existen
    owner_group, _ = Group.objects.get_or_create(name='owner')
    receptionist_group, _ = Group.objects.get_or_create(name='receptionist')
    veterinarian_group, _ = Group.objects.get_or_create(name='veterinarian')
    manager_group, _ = Group.objects.get_or_create(name='manager')
    tech_group, _ = Group.objects.get_or_create(name='technician')
    vet_tech_group, _ = Group.objects.get_or_create(name='veterinary_technician')

    # 3. Asegurar que todos los usuarios en la base de datos tengan consistencia
    print("Normalizando y asegurando consistencia de usuarios existentes...")
    for user in User.objects.all():
        group_names = set(user.groups.values_list('name', flat=True))
        
        # Cada usuario debe tener una persona natural
        np, _ = NaturalPerson.objects.get_or_create(
            user=user,
            defaults={
                'phone': '+541155554444',
                'address': 'Dirección por defecto',
                'dni': '12345678'
            }
        )
        
        if 'owner' in group_names:
            Owner.objects.get_or_create(
                user=user,
                defaults={
                    'natural_person': np,
                    'location': 'Sede Palermo',
                    'emergency_contact': '+541155559999'
                }
            )
        
        staff_roles = {'veterinarian', 'receptionist', 'manager', 'technician', 'veterinary_technician'}
        is_staff_role = bool(group_names & staff_roles) or user.is_staff or user.is_superuser
        
        if is_staff_role:
            clinical_staff, _ = ClinicalStaff.objects.get_or_create(
                user=user,
                defaults={'natural_person': np}
            )
            if 'veterinarian' in group_names:
                Veterinarian.objects.get_or_create(
                    clinical_staff=clinical_staff,
                    defaults={'specialty': 'Cirugía General'}
                )
    
    # 4. Asegurar que existan los usuarios específicos del seed (si no existen se crean)
    # Carlos Mendoza (Owner)
    owner_user, created = User.objects.get_or_create(
        email='propietario@petcare.com',
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
    owner_np, _ = NaturalPerson.objects.get_or_create(user=owner_user)
    owner_np.phone = '+541155554444'
    owner_np.address = 'Av. Libertador 1420, CABA'
    owner_np.dni = '35123456'
    owner_np.save()
    owner_profile, _ = Owner.objects.get_or_create(
        user=owner_user,
        defaults={'natural_person': owner_np, 'location': 'Sede Palermo', 'emergency_contact': '+541155559999'}
    )

    # Ana Gómez (Receptionist)
    receptionist_user, created = User.objects.get_or_create(
        email='recepcion@petcare.com',
        defaults={
            'username': 'ana_gomez',
            'first_name': 'Ana',
            'last_name': 'Gómez',
            'is_active': True
        }
    )
    if created:
        receptionist_user.set_password('petcare123')
        receptionist_user.save()
    receptionist_user.groups.add(receptionist_group)
    receptionist_np, _ = NaturalPerson.objects.get_or_create(user=receptionist_user)
    receptionist_np.phone = '+541155552222'
    receptionist_np.address = 'Sede Centro'
    receptionist_np.dni = '28456123'
    receptionist_np.save()
    ClinicalStaff.objects.get_or_create(user=receptionist_user, defaults={'natural_person': receptionist_np})

    # Dr. Luis Paz (Veterinarian)
    vet_user, created = User.objects.get_or_create(
        email='vet@petcare.com',
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
    vet_np, _ = NaturalPerson.objects.get_or_create(user=vet_user)
    vet_np.phone = '+541155553333'
    vet_np.address = 'Sede Palermo'
    vet_np.dni = '30123789'
    vet_np.save()
    vet_staff, _ = ClinicalStaff.objects.get_or_create(user=vet_user, defaults={'natural_person': vet_np})
    vet_profile, _ = Veterinarian.objects.get_or_create(clinical_staff=vet_staff, defaults={'specialty': 'Cirugía General'})

    # Admin Gerente (Manager)
    manager_user, created = User.objects.get_or_create(
        email='admin@petcare.com',
        defaults={
            'username': 'admin_gerente',
            'first_name': 'Admin',
            'last_name': 'Gerente',
            'is_active': True,
            'is_staff': True,
            'is_superuser': False
        }
    )
    if created:
        manager_user.set_password('petcare123')
        manager_user.save()
    else:
        manager_user.is_superuser = False
        manager_user.is_staff = True
        manager_user.save()
    manager_user.groups.add(manager_group)
    manager_np, _ = NaturalPerson.objects.get_or_create(user=manager_user)
    ClinicalStaff.objects.get_or_create(user=manager_user, defaults={'natural_person': manager_np})

    # Técnico de Inventario (Technician)
    tech_user, created = User.objects.get_or_create(
        email='tecnico@petcare.com',
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
    tech_np, _ = NaturalPerson.objects.get_or_create(user=tech_user)
    ClinicalStaff.objects.get_or_create(user=tech_user, defaults={'natural_person': tech_np})

    # Super Administrador (SuperAdmin)
    superadmin_user, created = User.objects.get_or_create(
        email='superadmin@petcare.com',
        defaults={
            'username': 'super_admin',
            'first_name': 'Super',
            'last_name': 'Administrador',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True
        }
    )
    superadmin_user.is_superuser = True
    superadmin_user.is_staff = True
    superadmin_user.set_password('petcare123')
    superadmin_user.save()
    superadmin_np, _ = NaturalPerson.objects.get_or_create(user=superadmin_user)
    ClinicalStaff.objects.get_or_create(user=superadmin_user, defaults={'natural_person': superadmin_np})

    print("Usuarios y roles base asegurados.")

    # 5. Crear Proveedores (Supplier)
    print("Creando proveedores...")
    # NOTA CRÍTICA: Debe existir el proveedor con la UUID hardcodeada del frontend
    supplier_frontend, _ = Supplier.objects.get_or_create(
        id='554d23aa-4a60-4186-abfb-bdbc01312256',
        defaults={
            'name': 'Distribuidora Global Veterinaria',
            'contact_name': 'Andrés Gómez',
            'phone': '+541166667777',
            'email': 'ventas@globalvet.com',
            'address': 'Parque Industrial Norte, CABA'
        }
    )
    
    supplier_alternative, _ = Supplier.objects.get_or_create(
        name='Farmacia Veterinaria Central',
        defaults={
            'contact_name': 'Sofía Martínez',
            'phone': '0800-555-8387',
            'email': 'ventas@farmaciavet.com',
            'address': 'Industrial Park Sector B'
        }
    )

    # 6. Crear Insumos (Supply)
    print("Creando insumos y existencias...")
    # Medicamentos
    s_amox = Supply.objects.create(sku='MED-AMOX-500', name='Amoxicilina 500mg', category='MEDICINE', min_stock=50, description='Antibiótico de amplio espectro')
    s_melo = Supply.objects.create(sku='MED-MELO-15', name='Meloxicam 15mg', category='MEDICINE', min_stock=30, description='Antiinflamatorio no esteroideo')
    
    # Vacunas
    s_rab = Supply.objects.create(sku='VAC-RAB-01', name='Vacuna Antirrábica', category='VACCINE', min_stock=40, description='Inmunización contra el virus de la rabia')
    s_trp = Supply.objects.create(sku='VAC-TRP-02', name='Vacuna Triple Felina', category='VACCINE', min_stock=25, description='Vacuna triple felina (calicivirus, rinotraqueitis, panleucopenia)')
    s_pav = Supply.objects.create(sku='VAC-PAV-03', name='Vacuna Parvovirus Canino', category='VACCINE', min_stock=35, description='Inmunización contra parvovirosis')

    # Consumibles
    s_gua = Supply.objects.create(sku='CON-GUA-LIT', name='Guantes de Látex', category='CONSUMABLE', min_stock=100, description='Guantes estériles desechables')
    s_jer = Supply.objects.create(sku='CON-JER-3ML', name='Jeringas de 3ml', category='CONSUMABLE', min_stock=150, description='Jeringas estériles con aguja')

    # 7. Crear Lotes (SupplyBatch)
    today = date.today()
    # Lotes saludables
    SupplyBatch.objects.create(supply=s_amox, lot_number='L-AMOX-01', expiration_date=today + timedelta(days=400), initial_stock=120, current_stock=90, acquisition_cost=Decimal('1.50'))
    SupplyBatch.objects.create(supply=s_melo, lot_number='L-MELO-02', expiration_date=today + timedelta(days=360), initial_stock=50, current_stock=45, acquisition_cost=Decimal('2.20'))
    SupplyBatch.objects.create(supply=s_rab, lot_number='L-RAB-03', expiration_date=today + timedelta(days=500), initial_stock=100, current_stock=80, acquisition_cost=Decimal('4.50'))
    
    # Lote en Alerta Crítica de Cantidad (Triple felina actual stock 12 < min_stock 25)
    SupplyBatch.objects.create(supply=s_trp, lot_number='L-TRP-04', expiration_date=today + timedelta(days=200), initial_stock=30, current_stock=12, acquisition_cost=Decimal('6.00'))
    
    # Lote en Alerta de Vencimiento (Guantes de Látex vence en 15 días)
    SupplyBatch.objects.create(supply=s_gua, lot_number='L-GUA-05', expiration_date=today + timedelta(days=15), initial_stock=200, current_stock=180, acquisition_cost=Decimal('0.10'))
    
    # Otro lote saludable para Guantes para suplir stock
    SupplyBatch.objects.create(supply=s_gua, lot_number='L-GUA-06', expiration_date=today + timedelta(days=600), initial_stock=300, current_stock=250, acquisition_cost=Decimal('0.12'))
    
    # Jeringas
    SupplyBatch.objects.create(supply=s_jer, lot_number='L-JER-07', expiration_date=today + timedelta(days=700), initial_stock=400, current_stock=350, acquisition_cost=Decimal('0.05'))

    # 8. Crear Pacientes (Pets)
    print("Creando pacientes (mascotas)...")
    # Toby de Carlos Mendoza
    p_toby = Patient.objects.create(
        name='Toby',
        species_breed='Canino - Golden Retriever',
        gender='Macho',
        birth_date=today - timedelta(days=3*365), # 3 años
        current_weight=32.5,
        owner=owner_profile,
        physical_marks='Mancha blanca en el pecho, collar azul',
        microchip_id='98100023412',
        reproductive_status='Neutered'
    )
    
    # Luna de Carlos Mendoza
    p_luna = Patient.objects.create(
        name='Luna',
        species_breed='Felino - Siamés',
        gender='Hembra',
        birth_date=today - timedelta(days=2*365), # 2 años
        current_weight=4.1,
        owner=owner_profile,
        physical_marks='Ojos azules intensos, puntas oscuras',
        microchip_id='98100023413',
        reproductive_status='Spayed'
    )

    # Rocky de cesar@gmail.com
    owner_cesar = Owner.objects.filter(user__email='cesar@gmail.com').first()
    p_rocky = Patient.objects.create(
        name='Rocky',
        species_breed='Canino - Pastor Alemán',
        gender='Macho',
        birth_date=today - timedelta(days=4*365),
        current_weight=38.0,
        owner=owner_cesar if owner_cesar else owner_profile,
        physical_marks='Cicatriz pequeña en la oreja derecha',
        microchip_id='98100023414',
        reproductive_status='Intact'
    )

    # 9. Crear Expedientes Clínicos (ClinicalRecords)
    ClinicalRecords.objects.create(patient=p_toby, opened_at=today - timedelta(days=100), allergies_history='Ninguna conocida', medical_alerts='Sensible a picaduras de pulga')
    ClinicalRecords.objects.create(patient=p_luna, opened_at=today - timedelta(days=90), allergies_history='Reacción leve a vacuna antirrábica previa', medical_alerts='Controlar temperatura posvacunal')
    ClinicalRecords.objects.create(patient=p_rocky, opened_at=today - timedelta(days=80), allergies_history='Alérgico a la penicilina', medical_alerts='ALERTA: Alergia grave a penicilina')

    # 10. Crear Planes de Vacunación (VaccinationPlan)
    plan_toby = VaccinationPlan.objects.create(patient=p_toby, vet=vet_profile, is_active=True)
    VaccinationPlanItem.objects.create(plan=plan_toby, vaccine_name='Vacuna Antirrábica', target_age_days=365)
    VaccinationPlanItem.objects.create(plan=plan_toby, vaccine_name='Vacuna Parvovirus Canino', target_age_days=180)

    # 11. Crear Agendas (VetSchedule) y Turnos (TimeSlots)
    print("Creando turnos y agenda para Dr. Luis Paz...")
    # Agenda para hoy
    schedule_today = VetSchedule.objects.create(vet=vet_profile, start_date=today, end_date=today)
    
    # Turno 1 (Hoy - Completado) -> Conectado a Toby
    slot1 = TimeSlot.objects.create(schedule=schedule_today, start_time='09:00:00', end_time='09:30:00', status='BOOKED')
    appt1 = Appointment.objects.create(slot=slot1, patient=p_toby, reason_for_visit='Vacuna de rutina y pesaje', status='COMPLETED')
    
    # Registrar evento de vacunación para Toby en el turno completado
    VaccinationDewormingEvent.objects.create(
        plan=plan_toby,
        consultation=appt1,
        event_type='VACCINE',
        vaccine_name='Vacuna Antirrábica',
        dose='1 dosis (0.5ml)',
        applied_date=today,
        sanitary_batch='L-RAB-03',
        next_due_date=today + timedelta(days=365)
    )

    # Turno 2 (Hoy - En Sala) -> Conectado a Rocky
    slot2 = TimeSlot.objects.create(schedule=schedule_today, start_time='10:00:00', end_time='10:30:00', status='BOOKED')
    appt2 = Appointment.objects.create(slot=slot2, patient=p_rocky, reason_for_visit='Consulta por renguera pata trasera', status='CHECKED_IN')
    WaitingListEntry.objects.create(patient=p_rocky, appointment=appt2, priority_level='MEDIUM', status='WAITING')

    # Turno 3 (Hoy - Confirmado) -> Conectado a Luna
    slot3 = TimeSlot.objects.create(schedule=schedule_today, start_time='11:00:00', end_time='11:30:00', status='BOOKED')
    Appointment.objects.create(slot=slot3, patient=p_luna, reason_for_visit='Control general de salud', status='CONFIRMED')

    # Turno 4 (Hoy - Libre)
    TimeSlot.objects.create(schedule=schedule_today, start_time='12:00:00', end_time='12:30:00', status='FREE')
    # Turno 5 (Hoy - Libre)
    TimeSlot.objects.create(schedule=schedule_today, start_time='15:00:00', end_time='15:30:00', status='FREE')

    # Agenda para mañana (Turnos programados futuros)
    schedule_tomorrow = VetSchedule.objects.create(vet=vet_profile, start_date=today + timedelta(days=1), end_date=today + timedelta(days=1))
    
    # Turno mañana (Reservado / Programado) -> Toby
    slot_tom = TimeSlot.objects.create(schedule=schedule_tomorrow, start_time='09:30:00', end_time='10:00:00', status='BOOKED')
    Appointment.objects.create(slot=slot_tom, patient=p_toby, reason_for_visit='Seguimiento clínico general', status='SCHEDULED')
    
    # Turno mañana (Libre)
    TimeSlot.objects.create(schedule=schedule_tomorrow, start_time='11:00:00', end_time='11:30:00', status='FREE')

    # 12. Crear Requisiciones y Órdenes de Compra (PurchaseOrders) para el Dashboard
    print("Creando órdenes de compra e historial de adquisiciones...")
    # Orden de compra 1: Recibida (Completada esta semana) -> Cuenta para presupuesto de compras
    po_rec = PurchaseOrder.objects.create(
        manager=manager_user,
        supplier=supplier_frontend,
        total_cost=Decimal('450.00'),
        status='RECEIVED'
    )
    PurchaseOrderItem.objects.create(order=po_rec, supply=s_rab, quantity_requested=100, unit_cost=Decimal('4.50'))

    # Orden de compra 2: Aprobada (Pendiente de recibir, esta semana)
    po_app = PurchaseOrder.objects.create(
        manager=manager_user,
        supplier=supplier_frontend,
        total_cost=Decimal('75.00'),
        status='APPROVED'
    )
    PurchaseOrderItem.objects.create(order=po_app, supply=s_amox, quantity_requested=50, unit_cost=Decimal('1.50'))

    # Orden de compra 3: Solicitada (Pendiente en seguimiento, hoy)
    po_req = PurchaseOrder.objects.create(
        manager=manager_user,
        supplier=supplier_frontend,
        total_cost=Decimal('18.00'),
        status='REQUESTED'
    )
    PurchaseOrderItem.objects.create(order=po_req, supply=s_trp, quantity_requested=3, unit_cost=Decimal('6.00'))

    print("Datos de prueba de negocio sembrados con éxito.")
    print("------------------------------------------------------------------")
    print("RESUMEN SEMBRADO:")
    print("- Proveedores: Distribuidora Global Veterinaria (Frontend ID) y Farmacia Veterinaria Central")
    print("- Insumos: 5 (MED-AMOX-500, MED-MELO-15, VAC-RAB-01, VAC-TRP-02, CON-GUA-LIT, CON-JER-3ML)")
    print("- Alertas: 1 por bajo stock (Triple Felina, stock 12 < min 25) y 1 por vencimiento (Guantes Lote L-GUA-05)")
    print("- Pacientes: Toby, Luna (Carlos Mendoza) y Rocky (Cesar)")
    print("- Turnos para hoy: 1 Completado (Toby), 1 En Sala (Rocky con espera), 1 Confirmado (Luna) y 2 Libres")
    print("- Turnos para mañana: 1 Programado (Toby) y 1 Libre")
    print("- Requisiciones / OC: 1 Recibida ($450), 1 Aprobada ($75) y 1 Pendiente ($18)")
    print("------------------------------------------------------------------")

if __name__ == '__main__':
    seed_data()
