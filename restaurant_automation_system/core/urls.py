from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ping,
    MenuItemViewSet, OrderViewSet, OrderDetailViewSet,
    IngredientViewSet, ItemIngredientViewSet, InventoryViewSet,
    PurchaseOrderViewSet, InvoiceViewSet, ChequeViewSet
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
    path("ping/", ping, name="ping"),
    path("", include(router.urls)),  # include all the API routes
]
