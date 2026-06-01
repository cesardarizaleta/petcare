from rest_framework import serializers
from django.db import models
from django.utils import timezone
from apps.stock.models import Supply, SupplyBatch

class BatchCreateFromFrontendSerializer(serializers.Serializer):
    insumoId = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1) 
    batch = serializers.CharField(max_length=50)
    expirationDate = serializers.DateField()
    acquisitionCost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    details = serializers.CharField(required=False, allow_blank=True, default='')
    observations = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_expirationDate(self, value):
        if value <= timezone.now().date():
            raise serializers.ValidationError("La fecha de vencimiento no puede ser pasada o igual a hoy.")
        return value

    def validate_insumoId(self, value):
        try:
            Supply.objects.get(id=value)
        except Supply.DoesNotExist:
            raise serializers.ValidationError("Insumo no encontrado.")
        return value

class BatchReadSerializer(serializers.ModelSerializer):
    batch = serializers.CharField(source='lot_number')
    expirationDate = serializers.DateField(source='expiration_date')
    quantity = serializers.IntegerField(source='current_stock')
    supply_name = serializers.CharField(source='supply.name', read_only=True)
    supply_sku = serializers.CharField(source='supply.sku', read_only=True)

    class Meta:
        model = SupplyBatch
        fields = ['id', 'supply', 'supply_name', 'supply_sku', 'batch', 'expirationDate', 'quantity', 'initial_stock', 'acquisition_cost', 'created_at']

class AlertItemSerializer(serializers.Serializer):
    supply_id = serializers.UUIDField()
    supply_name = serializers.CharField()
    supply_sku = serializers.CharField()
    alert_type = serializers.CharField()
    severity = serializers.CharField()
    message = serializers.CharField()
    current_value = serializers.IntegerField()
    threshold_value = serializers.IntegerField(required=False)
    days_remaining = serializers.IntegerField(required=False)
    batch_id = serializers.UUIDField(required=False)
    lot_number = serializers.CharField(required=False)


class SupplyReadSerializer(serializers.ModelSerializer):
    """Read serializer that includes computed stock from active batches."""
    quantity = serializers.SerializerMethodField()
    unitCost = serializers.SerializerMethodField()
    umbral = serializers.IntegerField(source='min_stock')
    type = serializers.CharField(source='get_category_display')
    batches = serializers.SerializerMethodField()

    class Meta:
        model = Supply
        fields = ['id', 'sku', 'name', 'type', 'category', 'description', 'quantity', 'unitCost', 'umbral', 'batches']

    def get_quantity(self, obj):
        today = timezone.now().date()
        total = obj.batches.filter(
            expiration_date__gt=today, current_stock__gt=0
        ).aggregate(total=models.Sum('current_stock'))['total']
        return total or 0

    def get_unitCost(self, obj):
        latest = obj.batches.order_by('-created_at').first()
        if latest:
            return float(latest.acquisition_cost)
        return 0.0

    def get_batches(self, obj):
        today = timezone.now().date()
        active_batches = obj.batches.filter(
            expiration_date__gt=today, current_stock__gt=0
        ).order_by('expiration_date')
        return [{
            'batch': b.lot_number,
            'expirationDate': str(b.expiration_date),
            'quantity': b.current_stock,
            'initialStock': b.initial_stock,
        } for b in active_batches]


class SupplyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    category = serializers.ChoiceField(choices=Supply.CATEGORY_CHOICES)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    min_stock = serializers.IntegerField(min_value=1, default=10)
    sku = serializers.CharField(max_length=50, required=False)
    initial_stock = serializers.IntegerField(min_value=0, required=False, default=0)

    def validate_sku(self, value):
        if value and Supply.objects.filter(sku=value).exists():
            raise serializers.ValidationError('Ya existe un insumo con este SKU.')
        return value

    def create(self, validated_data):
        initial_stock = validated_data.pop('initial_stock', 0)
        if not validated_data.get('sku'):
            import uuid
            validated_data['sku'] = f"SKU-{str(uuid.uuid4())[:8].upper()}"
        supply = Supply.objects.create(**validated_data)

        if initial_stock > 0:
            import datetime
            from decimal import Decimal
            SupplyBatch.objects.create(
                supply=supply,
                lot_number="LOTE-INICIAL",
                expiration_date=datetime.date.today() + datetime.timedelta(days=365),
                initial_stock=initial_stock,
                current_stock=initial_stock,
                acquisition_cost=Decimal("0.00")
            )
        return supply


class SupplyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supply
        fields = ['name', 'category', 'description', 'min_stock', 'sku']
        extra_kwargs = {
            'name': {'required': False},
            'category': {'required': False},
            'sku': {'required': False},
        }
