from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.db import models
from django.db.models import F  # <-- ✅ Add this

from .models import (
    MenuItem, Order, OrderDetail, Ingredient, ItemIngredient,
    Inventory, PurchaseOrder, Invoice, Cheque
)

from .serializers import (
    MenuItemSerializer, OrderSerializer, OrderDetailSerializer,
    IngredientSerializer, ItemIngredientSerializer, InventorySerializer,
    PurchaseOrderSerializer, InvoiceSerializer, ChequeSerializer
)
@api_view(['GET'])
def low_stock_alerts(request):
    low_stock_items = Inventory.objects.filter(quantity_in_stock__lte=F('ingredient__threshold'))
    serializer = InventorySerializer(low_stock_items, many=True)
    return Response(serializer.data)

def ping(request):
    return JsonResponse({"message": "pong"})


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class ItemIngredientViewSet(viewsets.ModelViewSet):
    queryset = ItemIngredient.objects.all()
    serializer_class = ItemIngredientSerializer


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['ingredient__name', 'quantity_in_stock']
    ordering_fields = ['quantity_in_stock']
    search_fields = ['ingredient__name']


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class ChequeViewSet(viewsets.ModelViewSet):
    queryset = Cheque.objects.all()
    serializer_class = ChequeSerializer
