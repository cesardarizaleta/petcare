# backend/apps/reporting/tests.py
import json
from datetime import date, time, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import ClinicalStaff, Veterinarian, NaturalPerson
from apps.owners.models import Owner
from apps.patients.models import Patient
from apps.appointments.models import VetSchedule, TimeSlot, Appointment
from apps.stock.models import Supplier, Supply, SupplyBatch, PurchaseOrder

User = get_user_model()

class ReportingTestCase(APITestCase):
    def setUp(self):
        # 1. Create groups
        self.owner_group, _ = Group.objects.get_or_create(name='owner')
        self.manager_group, _ = Group.objects.get_or_create(name='manager')

        # 2. Create Manager User
        self.manager_user = User.objects.create_user(
            email='manager_test@petcare.com',
            password='Password123!',
            first_name='Admin',
            last_name='Gerente',
            is_active=True
        )
        self.manager_user.groups.add(self.manager_group)

        # 3. Create Owner User & Pet
        self.owner_user = User.objects.create_user(
            email='owner_test@petcare.com',
            password='Password123!',
            first_name='Carlos',
            last_name='Mendoza',
            is_active=True
        )
        self.owner_user.groups.add(self.owner_group)
        self.owner_np = NaturalPerson.objects.create(
            user=self.owner_user, phone='1234', address='Av 123', dni='DNI123'
        )
        self.owner_profile = Owner.objects.create(
            user=self.owner_user, natural_person=self.owner_np
        )

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

        # 4. Create Veterinarian
        self.vet_user = User.objects.create_user(
            email='vet_test@petcare.com',
            password='Password123!',
            first_name='Dr. Luis',
            last_name='Paz',
            is_active=True
        )
        self.vet_np = NaturalPerson.objects.create(
            user=self.vet_user, phone='5678', address='Av 456', dni='DNI456'
        )
        self.vet_staff = ClinicalStaff.objects.create(
            user=self.vet_user, natural_person=self.vet_np
        )
        self.vet_profile = Veterinarian.objects.create(
            clinical_staff=self.vet_staff, specialty='Cirugía'
        )

        # 5. Create Vet Schedule and Time slots
        self.today = timezone.localtime(timezone.now()).date()
        self.schedule = VetSchedule.objects.create(
            vet=self.vet_profile,
            start_date=self.today,
            end_date=self.today
        )
        
        self.slot1 = TimeSlot.objects.create(
            schedule=self.schedule,
            start_time=time(10, 0),
            end_time=time(10, 30),
            status='BOOKED'
        )
        self.slot2 = TimeSlot.objects.create(
            schedule=self.schedule,
            start_time=time(11, 0),
            end_time=time(11, 30),
            status='BOOKED'
        )

        # 6. Create Appointments
        self.appointment1 = Appointment.objects.create(
            slot=self.slot1,
            patient=self.patient,
            reason_for_visit='Control Mensual',
            status='COMPLETED'
        )
        self.appointment2 = Appointment.objects.create(
            slot=self.slot2,
            patient=self.patient,
            reason_for_visit='Vacunas',
            status='SCHEDULED'
        )

        # 7. Create Supplier & Stock & Batches
        self.supplier = Supplier.objects.create(
            name='Droguería Central',
            phone='44445555',
            email='contacto@drogueria.com',
            address='Calle Falsa 123'
        )

        self.supply_medicine = Supply.objects.create(
            sku='MED-100',
            name='Amoxicilina 500mg',
            description='Antibiótico de amplio espectro',
            category='MEDICINE',
            min_stock=10
        )

        # Critical low stock item (active stock = 5 <= min_stock=15)
        self.supply_critical = Supply.objects.create(
            sku='VAC-200',
            name='Vacuna Antirrábica',
            description='Vacuna anual',
            category='VACCINE',
            min_stock=15
        )

        self.batch_med = SupplyBatch.objects.create(
            supply=self.supply_medicine,
            lot_number='LOTE-A',
            expiration_date=self.today + timedelta(days=90),
            initial_stock=50,
            current_stock=35, # Consumed: 15
            acquisition_cost=Decimal('12.50')
        )

        self.batch_critical = SupplyBatch.objects.create(
            supply=self.supply_critical,
            lot_number='LOTE-B',
            expiration_date=self.today + timedelta(days=90),
            initial_stock=5,
            current_stock=5, # Consumed: 0 (stock is 5, min_stock is 15 -> Critical!)
            acquisition_cost=Decimal('25.00')
        )

        # 8. Create Purchase Orders
        self.po1 = PurchaseOrder.objects.create(
            supplier=self.supplier,
            total_cost=Decimal('450.00'),
            status='APPROVED'
        )
        # Create it today
        self.po1.created_at = timezone.now()
        self.po1.save()

    def test_unauthenticated_fails(self):
        """Verify endpoints are protected by default authentication."""
        response = self.client.get('/api/v1/reporting/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_summary_calculation(self):
        """Verify the KPI numbers and revenue graph calculations are correct."""
        self.client.force_authenticate(user=self.manager_user)
        
        response = self.client.get('/api/v1/reporting/dashboard/', {'periodo': 'este_mes'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['period'], 'este_mes')
        self.assertTrue(data['has_data'])

        # Validate KPIs structure and values
        kpis = {kpi['id']: kpi for kpi in data['kpis']}
        
        # 1. Presupuesto de compras should be po1 cost
        self.assertEqual(kpis['brecha']['value'], '$450.00')
        
        # 2. Desabastecimiento should be 1 (supply_critical only, as active stock=5 <= min_stock=15)
        self.assertEqual(kpis['stock']['value'], '1')
        
        # 3. Consultas realizadas should be 1 (appointment1 is completed, appointment2 is scheduled)
        self.assertEqual(kpis['ingresos']['value'], '1')
        
        # 4. Consumo de inventario should be batch_med consumed stock (50 - 35 = 15)
        self.assertEqual(kpis['consumo']['value'], '15')
        
        # 5. Efectividad: 1 completed out of 2 total -> 50%
        self.assertEqual(kpis['citas']['value'], '50%')

        # Validate revenue data
        revenue = data['revenueData']
        self.assertTrue(len(revenue) > 0)
        self.assertEqual(revenue[0]['amount'], 450.00)

    def test_kpi_list_endpoint(self):
        """Verify the dedicated KPI list endpoint returns the expected array."""
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get('/api/v1/reporting/kpis/', {'periodo': 'hoy'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(len(response.data), 5)

    def test_revenue_chart_endpoint(self):
        """Verify the revenue endpoint works and yields correct date points."""
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get('/api/v1/reporting/revenue/', {'periodo': 'esta_semana'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))

    def test_export_report_csv(self):
        """Verify CSV reporting format generation and content headers."""
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get('/api/v1/reporting/export/', {'periodo': 'este_mes', 'export_format': 'csv'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8-sig')
        self.assertTrue('attachment' in response['Content-Disposition'])
        
        content = response.content.decode('utf-8-sig')
        self.assertTrue('REPORTE DE DESEMPEÑO' in content)
        self.assertTrue('Presupuesto de Compras' in content)
        self.assertTrue('Firu' in content) # Patient name should be inside appointments log
        self.assertTrue('Droguería Central' in content) # Supplier name should be inside purchases log

    def test_export_report_json(self):
        """Verify JSON reporting format generation and payload fields."""
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get('/api/v1/reporting/export/', {'periodo': 'este_mes', 'export_format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
        
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue('report_metadata' in data)
        self.assertTrue('kpis' in data)
        self.assertEqual(len(data['appointments']), 2)
        self.assertEqual(len(data['purchase_orders']), 1)
        self.assertEqual(data['appointments'][0]['patient_name'], 'Firu')
        self.assertEqual(data['purchase_orders'][0]['supplier_name'], 'Droguería Central')

    def test_custom_date_range(self):
        """Verify custom date ranges via 'from' and 'to' query parameters work correctly."""
        self.client.force_authenticate(user=self.manager_user)
        
        # Format today and tomorrow dates in YYYY-MM-DD
        from_str = str(self.today)
        to_str = str(self.today + timedelta(days=1))
        
        response = self.client.get('/api/v1/reporting/dashboard/', {
            'from': from_str,
            'to': to_str
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['from'], from_str)
        self.assertEqual(data['to'], to_str)
        self.assertTrue(data['has_data'])

