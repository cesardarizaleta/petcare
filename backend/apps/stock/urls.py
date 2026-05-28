from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.stock.views import SupplyBatchCreateView, InventoryAlertsView, InventoryConsumeView
from apps.stock.views_orders import PurchaseOrderViewSet

router = DefaultRouter()
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-orders')

urlpatterns = [
    path('batches/', SupplyBatchCreateView.as_view(), name='inventory-batches'),
    path('alerts/', InventoryAlertsView.as_view(), name='inventory-alerts'),
    path('consume/', InventoryConsumeView.as_view(), name='inventory-consume'),
    path('', include(router.urls)),
]
