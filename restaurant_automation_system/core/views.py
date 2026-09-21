from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import (
    MenuItem, Order, OrderDetail, Ingredient, ItemIngredient,
    Inventory, PurchaseOrder, Invoice, Cheque, RestaurantTable, Reservation
)
from .serializers import (
    MenuItemSerializer, OrderSerializer, OrderDetailSerializer,
    IngredientSerializer, ItemIngredientSerializer, InventorySerializer,
    PurchaseOrderSerializer, InvoiceSerializer, ChequeSerializer,
    RestaurantTableSerializer, ReservationSerializer
)


@api_view(['GET'])
def low_stock_alerts(request):
    inventory_items = Inventory.objects.select_related('ingredient').all()
    low_stock_items = [
        item
        for item in inventory_items
        if item.quantity_in_stock <= item.ingredient.calculate_threshold()
    ]
    serializer = InventorySerializer(low_stock_items, many=True)
    return Response(serializer.data)


def ping(request):
    return JsonResponse({'message': 'pong'})


class RestaurantTableViewSet(viewsets.ModelViewSet):
    queryset = RestaurantTable.objects.all().order_by('number')
    serializer_class = RestaurantTableSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related('table').order_by('-reservation_at')
    serializer_class = ReservationSerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all().order_by('name')
    serializer_class = MenuItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related(
        'details__menu_item'
    ).select_related('salesclerk').order_by('-created_at')
    serializer_class = OrderSerializer


class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.select_related('order', 'menu_item').all()
    serializer_class = OrderDetailSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer


class ItemIngredientViewSet(viewsets.ModelViewSet):
    queryset = ItemIngredient.objects.select_related(
        'menu_item', 'ingredient'
    ).all()
    serializer_class = ItemIngredientSerializer


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related('ingredient').all()
    serializer_class = InventorySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter
    ]
    filterset_fields = ['ingredient__name', 'quantity_in_stock']
    ordering_fields = ['quantity_in_stock', 'ingredient__name']
    search_fields = ['ingredient__name']


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.select_related(
        'ingredient'
    ).order_by('-created_at')
    serializer_class = PurchaseOrderSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related(
        'purchase_order__ingredient'
    ).order_by('-received_at')
    serializer_class = InvoiceSerializer


class ChequeViewSet(viewsets.ModelViewSet):
    queryset = Cheque.objects.select_related(
        'invoice__purchase_order__ingredient'
    ).order_by('-issued_at')
    serializer_class = ChequeSerializer


@api_view(['GET'])
def menu_card(request):
    menu_items = MenuItem.objects.prefetch_related(
        'itemingredient_set__ingredient'
    ).filter(available=True)

    data = []
    for item in menu_items:
        ingredients = [
            {
                'name': item_ingredient.ingredient.name,
                'quantity_required': item_ingredient.quantity_required,
                'unit': item_ingredient.ingredient.unit,
            }
            for item_ingredient in item.itemingredient_set.all()
        ]

        data.append({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'ingredients': ingredients,
        })

    return Response(data)
