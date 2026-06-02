# backend/apps/reporting/reports.py
import datetime
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum
from apps.appointments.models import Appointment
from apps.stock.models import Supply, SupplyBatch, PurchaseOrder

def get_date_range(periodo, start_date=None, end_date=None):
    """
    Returns (start_date, end_date) as datetime.date objects for the selected period.
    """
    if start_date and end_date:
        if isinstance(start_date, str):
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        return start_date, end_date

    today = timezone.localtime(timezone.now()).date()

    if periodo == 'hoy':
        return today, today
    elif periodo == 'esta_semana':
        return today - datetime.timedelta(days=7), today
    elif periodo == 'este_mes':
        return today.replace(day=1), today
    else:
        # Default fallback to this month
        return today.replace(day=1), today

def calculate_kpis(start, end):
    """
    Calculates operational and tactical KPIs for the given date range.
    """
    today = timezone.localtime(timezone.now()).date()

    # 1. Presupuesto de Compras (Gasto real acumulado en requisiciones/compras)
    total_gasto = PurchaseOrder.objects.filter(
        created_at__date__gte=start,
        created_at__date__lte=end
    ).aggregate(total=Sum('total_cost'))['total'] or Decimal('0.00')
    total_gasto = float(total_gasto)

    # 2. Desabastecimiento (Insumos Críticos)
    insumos_criticos = 0
    for supply in Supply.objects.prefetch_related('batches').all():
        active_stock = supply.batches.filter(
            expiration_date__gt=today,
            current_stock__gt=0
        ).aggregate(total=Sum('current_stock'))['total'] or 0
        if active_stock <= supply.min_stock:
            insumos_criticos += 1

    # 3. Consultas Realizadas (Completed appointments)
    citas_completadas = Appointment.objects.filter(
        status='COMPLETED',
        slot__schedule__start_date__gte=start,
        slot__schedule__start_date__lte=end
    ).count()

    # 4. Consumo Inventario Real
    total_consumido = 0
    batches = SupplyBatch.objects.filter(
        created_at__date__gte=start,
        created_at__date__lte=end
    )
    for b in batches:
        if b.initial_stock > b.current_stock:
            total_consumido += (b.initial_stock - b.current_stock)

    # 5. Efectividad de Citas (Completed / Total in period)
    total_citas = Appointment.objects.filter(
        slot__schedule__start_date__gte=start,
        slot__schedule__start_date__lte=end
    ).count()
    porcentaje_citas = round((citas_completadas / total_citas) * 100) if total_citas > 0 else 0

    return [
        {
            "id": "brecha",
            "title": "Presupuesto de Compras",
            "value": f"${total_gasto:.2f}",
            "icon": "layout-dashboard",
            "status": "warning" if total_gasto > 1000 else "success",
        },
        {
            "id": "stock",
            "title": "Desabastecimiento",
            "value": str(insumos_criticos),
            "icon": "clipboard-list",
            "status": "danger" if insumos_criticos > 0 else "success",
        },
        {
            "id": "ingresos",
            "title": "Consultas Realizadas",
            "value": str(citas_completadas),
            "icon": "clipboard-check",
            "status": "success",
        },
        {
            "id": "consumo",
            "title": "Consumo Inventario",
            "value": str(total_consumido),
            "icon": "syringe",
            "status": "info",
        },
        {
            "id": "citas",
            "title": "Efectividad Citas",
            "value": f"{porcentaje_citas}%",
            "icon": "calendar-days",
            "status": "success" if porcentaje_citas > 50 else "warning",
        },
    ]

def get_revenue_data(start, end, periodo):
    """
    Returns aggregate purchase order costs grouped by date or month depending on period.
    """
    purchase_orders = PurchaseOrder.objects.filter(
        created_at__date__gte=start,
        created_at__date__lte=end
    ).order_by('created_at')

    grouped = {}
    for po in purchase_orders:
        date_str = po.created_at.date()
        if periodo == 'este_mes':
            # Group by Year-Month (e.g., '2026-06')
            key = date_str.strftime('%Y-%m')
        else:
            # Group by exact date (e.g., '2026-06-02')
            key = date_str.strftime('%Y-%m-%d')
        
        grouped[key] = grouped.get(key, 0.0) + float(po.total_cost)

    chart_points = [
        {"label": label, "amount": round(amount, 2)}
        for label, amount in sorted(grouped.items())
    ]

    if not chart_points:
        return [{"label": "Sin compras", "amount": 0.0}]

    return chart_points
