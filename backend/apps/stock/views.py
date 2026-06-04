import logging
import datetime
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from apps.stock.models import Supply, SupplyBatch
from apps.stock.serializers import BatchCreateFromFrontendSerializer, BatchReadSerializer
from apps.stock.services import consume_supply_fifo

logger = logging.getLogger(__name__)


class SupplyBatchCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BatchCreateFromFrontendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        validated = serializer.validated_data

        supply = Supply.objects.get(id=validated['insumoId'])
        
        acquisition_cost = validated.get('acquisitionCost')
        if not acquisition_cost:
            latest_batch = supply.batches.order_by('-created_at').first()
            acquisition_cost = latest_batch.acquisition_cost if (latest_batch and latest_batch.acquisition_cost > 0) else Decimal('10.00')
        elif acquisition_cost <= 0:
            acquisition_cost = Decimal('10.00')

        batch = SupplyBatch.objects.create(
            supply=supply,
            lot_number=validated['batch'],
            expiration_date=validated['expirationDate'],
            initial_stock=validated['quantity'],
            current_stock=validated['quantity'],
            acquisition_cost=acquisition_cost
        )

        read_serializer = BatchReadSerializer(batch)
        return Response({"message": "Lote registrado exitosamente.", "batch": read_serializer.data}, status=status.HTTP_201_CREATED)

    def get(self, request):
        queryset = SupplyBatch.objects.select_related('supply').all()
        serializer = BatchReadSerializer(queryset, many=True)
        return Response(serializer.data)


class InventoryAlertsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        alerts = []

        for supply in Supply.objects.all():
            active_stock = supply.batches.filter(expiration_date__gt=today, current_stock__gt=0).aggregate(total=Sum('current_stock'))['total'] or 0
            min_alert = supply.min_stock
            warning_threshold = int(min_alert * 1.5)

            if active_stock <= min_alert:
                alerts.append({"supply_id": supply.id, "supply_name": supply.name, "supply_sku": supply.sku, "alert_type": "LOW_STOCK", "severity": "critical", "message": f"CRÍTICO: '{supply.name}' tiene {active_stock} uds.", "current_value": active_stock})
            elif active_stock <= warning_threshold:
                alerts.append({"supply_id": supply.id, "supply_name": supply.name, "supply_sku": supply.sku, "alert_type": "LOW_STOCK", "severity": "warning", "message": f"ALERTA: '{supply.name}' tiene {active_stock} uds.", "current_value": active_stock})

        limit_date = today + datetime.timedelta(days=45)
        expiring_batches = SupplyBatch.objects.filter(expiration_date__gt=today, expiration_date__lte=limit_date, current_stock__gt=0).select_related('supply')

        for batch in expiring_batches:
            days_remaining = (batch.expiration_date - today).days
            severity = 'critical' if days_remaining <= 15 else 'warning'
            
            alerts.append({"supply_id": batch.supply.id, "supply_name": batch.supply.name, "supply_sku": batch.supply.sku, "alert_type": "NEAR_EXPIRATION", "severity": severity, "message": f"Lote '{batch.lot_number}' vence en {days_remaining} días.", "current_value": batch.current_stock})

        alerts.sort(key=lambda a: 0 if a['severity'] == 'critical' else 1)
        return Response({"alerts": alerts})


class InventoryConsumeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        supply_id = request.data.get('supply_id')
        quantity = request.data.get('quantity')
        consultation_id = request.data.get('consultation_id')

        if not supply_id or not quantity:
            return Response(
                {"error": "Los campos 'supply_id' y 'quantity' son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response(
                {"error": "La cantidad debe ser un número entero válido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            updated_supply = consume_supply_fifo(supply_id, quantity, consultation_id)
            
            # Calcular el stock total restante de este insumo para retornar en la respuesta
            active_stock = updated_supply.batches.filter(
                expiration_date__gt=timezone.now().date(), 
                current_stock__gt=0
            ).aggregate(total=Sum('current_stock'))['total'] or 0
            
            return Response({
                "message": "Consumo FIFO registrado con éxito.",
                "supply_id": updated_supply.id,
                "name": updated_supply.name,
                "remaining_stock": active_stock
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )


from rest_framework import viewsets
from apps.stock.serializers import SupplyReadSerializer, SupplyCreateSerializer, SupplyUpdateSerializer

class SupplyViewSet(viewsets.ModelViewSet):
    """CRUD completo para insumos del catálogo maestro."""
    permission_classes = [IsAuthenticated]
    queryset = Supply.objects.prefetch_related('batches').all().order_by('name')

    def get_serializer_class(self):
        if self.action == 'create':
            return SupplyCreateSerializer
        if self.action in ('update', 'partial_update'):
            return SupplyUpdateSerializer
        return SupplyReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = SupplyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        supply = serializer.save()
        read_serializer = SupplyReadSerializer(supply)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
