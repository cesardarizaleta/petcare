# backend/apps/reporting/views.py
import csv
import json
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .reports import get_date_range, calculate_kpis, get_revenue_data
from apps.appointments.models import Appointment
from apps.stock.models import PurchaseOrder, Supply
from django.db.models import Sum

class DashboardSummaryView(APIView):
    """
    GET /api/v1/reporting/dashboard/
    Returns combined operational KPIs and revenue/purchase chart data for the selected period.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        periodo = request.query_params.get('periodo', 'este_mes')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        try:
            start, end = get_date_range(periodo, start_date_str, end_date_str)
        except ValueError as e:
            return Response(
                {"error": f"Formato de fecha inválido. Use YYYY-MM-DD: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        kpis = calculate_kpis(start, end)
        revenue_data = get_revenue_data(start, end, periodo)

        # Check if there is any activity in the period to set has_data flag
        total_citas = Appointment.objects.filter(
            slot__schedule__start_date__gte=start,
            slot__schedule__start_date__lte=end
        ).count()
        total_requisiciones = PurchaseOrder.objects.filter(
            created_at__date__gte=start,
            created_at__date__lte=end
        ).count()

        has_data = (total_citas > 0 or total_requisiciones > 0)

        return Response({
            "period": periodo,
            "start_date": str(start),
            "end_date": str(end),
            "has_data": has_data,
            "kpis": kpis,
            "revenueData": revenue_data
        }, status=status.HTTP_200_OK)


class KPIListView(APIView):
    """
    GET /api/v1/reporting/kpis/
    Returns a list of real-time Key Performance Indicators.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        periodo = request.query_params.get('periodo', 'este_mes')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        try:
            start, end = get_date_range(periodo, start_date_str, end_date_str)
        except ValueError as e:
            return Response(
                {"error": f"Formato de fecha inválido. Use YYYY-MM-DD: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        kpis = calculate_kpis(start, end)
        return Response(kpis, status=status.HTTP_200_OK)


class RevenueChartView(APIView):
    """
    GET /api/v1/reporting/revenue/
    Returns data points for rendering the revenue/purchase chart.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        periodo = request.query_params.get('periodo', 'este_mes')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        try:
            start, end = get_date_range(periodo, start_date_str, end_date_str)
        except ValueError as e:
            return Response(
                {"error": f"Formato de fecha inválido. Use YYYY-MM-DD: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        revenue_data = get_revenue_data(start, end, periodo)
        return Response(revenue_data, status=status.HTTP_200_OK)


class ExportReportView(APIView):
    """
    GET /api/v1/reporting/export/
    Generates and exports an operational performance report for the selected range.
    Supports CSV and JSON formats.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        periodo = request.query_params.get('periodo', 'este_mes')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        export_format = request.query_params.get('export_format', 'csv').lower()

        try:
            start, end = get_date_range(periodo, start_date_str, end_date_str)
        except ValueError as e:
            return HttpResponse(
                f"Error: Formato de fecha inválido: {str(e)}", 
                status=400
            )

        # 1. Fetch KPI metrics
        kpis = calculate_kpis(start, end)
        
        # 2. Fetch Detailed Data for Report Content
        appointments = Appointment.objects.filter(
            slot__schedule__start_date__gte=start,
            slot__schedule__start_date__lte=end
        ).select_related('patient', 'patient__owner', 'patient__owner__user').order_by('slot__schedule__start_date')

        purchase_orders = PurchaseOrder.objects.filter(
            created_at__date__gte=start,
            created_at__date__lte=end
        ).select_related('supplier').order_by('created_at')

        # 3. CSV Export Format
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
            response['Content-Disposition'] = f'attachment; filename="reporte_desempeno_{periodo}_{start}_al_{end}.csv"'
            
            writer = csv.writer(response)
            
            # --- SECTION 1: HEADER & GENERAL METRICS ---
            writer.writerow(['=================================================='])
            writer.writerow(['REPORTE DE DESEMPEÑO Y RENDIMIENTO - CLINICA PETCARE'])
            writer.writerow(['=================================================='])
            writer.writerow(['Periodo del Reporte:', f'{start} al {end} ({periodo.upper()})'])
            writer.writerow(['Fecha de Generación:', str(timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S'))])
            writer.writerow([])
            
            writer.writerow(['INDICADORES CLAVE DE RENDIMIENTO (KPIs)'])
            writer.writerow(['Indicador', 'Valor'])
            for kpi in kpis:
                writer.writerow([kpi['title'], kpi['value']])
            writer.writerow([])

            # --- SECTION 2: DETAILED APPOINTMENTS LOG ---
            writer.writerow(['DETALLE DE CONSULTAS Y CITAS'])
            writer.writerow(['ID Cita', 'Fecha', 'Paciente', 'Propietario', 'Motivo de Visita', 'Estado'])
            if appointments.exists():
                for appt in appointments:
                    owner_name = ""
                    if appt.patient.owner:
                        user = appt.patient.owner.user
                        owner_name = f"{user.first_name} {user.last_name}".strip() or user.email
                    
                    writer.writerow([
                        appt.id,
                        str(appt.slot.schedule.start_date) if appt.slot else "",
                        appt.patient.name,
                        owner_name,
                        appt.reason_for_visit,
                        appt.get_status_display()
                    ])
            else:
                writer.writerow(['No se registraron consultas en este periodo.'])
            writer.writerow([])

            # --- SECTION 3: DETAILED PURCHASES LOG ---
            writer.writerow(['DETALLE DE REQUISICIONES Y COMPRAS'])
            writer.writerow(['ID Orden', 'Fecha', 'Proveedor', 'Costo Total ($)', 'Estado'])
            if purchase_orders.exists():
                for po in purchase_orders:
                    writer.writerow([
                        str(po.id),
                        po.created_at.strftime('%Y-%m-%d'),
                        po.supplier.name,
                        f"{float(po.total_cost):.2f}",
                        po.get_status_display()
                    ])
            else:
                writer.writerow(['No se registraron compras en este periodo.'])
            
            return response

        # 4. JSON Export Format
        elif export_format == 'json':
            # Map clean serializable structures
            serialized_appointments = []
            for appt in appointments:
                owner_name = ""
                if appt.patient.owner:
                    user = appt.patient.owner.user
                    owner_name = f"{user.first_name} {user.last_name}".strip() or user.email
                serialized_appointments.append({
                    "id": appt.id,
                    "date": str(appt.slot.schedule.start_date) if appt.slot else None,
                    "patient_name": appt.patient.name,
                    "owner_name": owner_name,
                    "reason": appt.reason_for_visit,
                    "status": appt.status
                })

            serialized_purchases = []
            for po in purchase_orders:
                serialized_purchases.append({
                    "id": str(po.id),
                    "date": po.created_at.strftime('%Y-%m-%d'),
                    "supplier_name": po.supplier.name,
                    "total_cost": float(po.total_cost),
                    "status": po.status
                })

            data = {
                "report_metadata": {
                    "period": periodo,
                    "start_date": str(start),
                    "end_date": str(end),
                    "generated_at": str(timezone.now())
                },
                "kpis": kpis,
                "appointments": serialized_appointments,
                "purchase_orders": serialized_purchases
            }

            response_content = json.dumps(data, indent=2, ensure_ascii=False)
            response = HttpResponse(response_content, content_type='application/json; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="reporte_desempeno_{periodo}_{start}_al_{end}.json"'
            return response

        else:
            return HttpResponse("Formatos válidos: 'csv' o 'json'", status=400)
