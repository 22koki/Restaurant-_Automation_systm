from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import (
    ping,
    MenuItemViewSet, OrderViewSet, OrderDetailViewSet,
    IngredientViewSet, ItemIngredientViewSet, InventoryViewSet,
    PurchaseOrderViewSet, InvoiceViewSet, ChequeViewSet,
    RestaurantTableViewSet, ReservationViewSet, PaymentViewSet, StaffProfileViewSet
)

router = DefaultRouter()
router.register(r'staff', StaffProfileViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'tables', RestaurantTableViewSet)
router.register(r'reservations', ReservationViewSet)
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
    path('api/low-stock/', views.low_stock_alerts),
    path('api/ping/', views.ping),
    path('api/auth/login/', views.staff_login),
    path('api/auth/logout/', views.staff_logout),
    path('api/auth/me/', views.staff_me),
    path('api/staff-directory/', views.staff_directory),
    path('api/menu-card/', views.menu_card),
    path('api/setup/', views.initial_setup),
    path('api/payments/mpesa/stk/', views.mpesa_stk_push),
    path('api/payments/mpesa/callback/', views.mpesa_callback),
]