from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    MenuItemViewSet, OrderViewSet, OrderDetailViewSet,
    IngredientViewSet, ItemIngredientViewSet, InventoryViewSet,
    PurchaseOrderViewSet, InvoiceViewSet, ChequeViewSet,
    low_stock_alerts, ping
)

router = DefaultRouter()
router.register(r'menu-items', MenuItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-details', OrderDetailViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'item-ingredients', ItemIngredientViewSet)
router.register(r'inventory', InventoryViewSet)
router.register(r'purchase-orders', PurchaseOrderViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'cheques', ChequeViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/low-stock/', low_stock_alerts, name='low-stock-alerts'),
    path('api/ping/', ping, name='ping'),
]
