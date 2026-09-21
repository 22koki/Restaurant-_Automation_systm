from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.db import transaction
from django.contrib.auth import authenticate

from .permissions import ActiveStaffPermission, OwnerManagerPermission, CashierManagerPermission, ServicePermission, KitchenPermission, InventoryPermission, staff_role
from .models import (
    MenuItem, Order, OrderDetail, Ingredient, ItemIngredient,
    Inventory, PurchaseOrder, Invoice, Cheque, RestaurantTable, Reservation, Payment, StaffProfile
)
from .serializers import (
    MenuItemSerializer, OrderSerializer, OrderDetailSerializer,
    IngredientSerializer, ItemIngredientSerializer, InventorySerializer,
    PurchaseOrderSerializer, InvoiceSerializer, ChequeSerializer,
    RestaurantTableSerializer, ReservationSerializer, PaymentSerializer, StaffProfileSerializer
)


@api_view(['GET'])
@permission_classes([InventoryPermission])
def low_stock_alerts(request):
    inventory_items = Inventory.objects.select_related('ingredient').all()
    low_stock_items = [
        item
        for item in inventory_items
        if item.quantity_in_stock <= item.ingredient.calculate_threshold()
    ]
    serializer = InventorySerializer(low_stock_items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def staff_login(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    user = authenticate(username=username, password=password)
    role = staff_role(user)
    if not user or not role:
        return Response({'detail': 'Invalid credentials or inactive staff account.'}, status=status.HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'name': user.get_full_name().strip() or user.username,
            'role': role,
        }
    })


@api_view(['POST'])
def staff_logout(request):
    if request.user.is_authenticated:
        Token.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([ActiveStaffPermission])
def staff_me(request):
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'name': request.user.get_full_name().strip() or request.user.username,
        'role': staff_role(request.user),
    })


def ping(request):
    return JsonResponse({'message': 'pong'})


@api_view(['POST'])
@permission_classes([OwnerManagerPermission])
@transaction.atomic
def initial_setup(request):
    table_count = int(request.data.get('table_count', 12))
    seats_per_table = int(request.data.get('seats_per_table', 4))
    area = request.data.get('area', 'Main Dining')
    seed_demo_menu = bool(request.data.get('seed_demo_menu', True))

    if table_count < 1 or table_count > 100:
        return Response(
            {'table_count': 'Choose between 1 and 100 tables.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    created_tables = 0
    for number in range(1, table_count + 1):
        _, created = RestaurantTable.objects.get_or_create(
            number=str(number),
            defaults={
                'seats': seats_per_table,
                'area': area,
                'status': 'available',
                'active': True,
            }
        )
        created_tables += int(created)

    created_menu_items = 0
    if seed_demo_menu:
        starter_menu = [
            ('Fire-Grilled Chicken', 'Chef Favourites', 'Herb butter, charred lemon and garden greens.', 1450, 'grill'),
            ('Truffle Mushroom Pasta', 'Pasta', 'Wild mushrooms, parmesan, cream and herbs.', 1280, 'kitchen'),
            ('Garden Burrata', 'Small Plates', 'Tomatoes, basil oil, toasted sourdough and sea salt.', 980, 'kitchen'),
            ('Smash Burger', 'Burgers', 'Beef patty, cheddar, pickles and house sauce.', 1250, 'grill'),
            ('Crispy Calamari', 'Small Plates', 'Lemon, chilli and garlic aioli.', 1100, 'kitchen'),
            ('Passion Mojito', 'Drinks', 'Passion fruit, lime and fresh mint.', 650, 'bar'),
        ]
        for name, category, description, price, station in starter_menu:
            _, created = MenuItem.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'description': description,
                    'price': price,
                    'prep_station': station,
                    'available': True,
                }
            )
            created_menu_items += int(created)

    return Response({
        'tables_created': created_tables,
        'menu_items_created': created_menu_items,
        'message': 'Restaurant setup completed.'
    })


class StaffProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [OwnerManagerPermission]
    queryset = StaffProfile.objects.select_related('user').order_by('role', 'user__first_name', 'user__username')
    serializer_class = StaffProfileSerializer


@api_view(['GET'])
@permission_classes([ActiveStaffPermission])
def staff_directory(request):
    profiles = StaffProfile.objects.select_related('user').filter(
        active=True,
        role__in=['waiter', 'cashier']
    ).order_by('role', 'user__first_name', 'user__username')
    return Response([
        {
            'user': profile.user_id,
            'name': profile.user.get_full_name().strip() or profile.user.username,
            'role': profile.role,
        }
        for profile in profiles
    ])


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [CashierManagerPermission]
    queryset = Payment.objects.select_related('order', 'order__table').order_by('-created_at')
    serializer_class = PaymentSerializer


class RestaurantTableViewSet(viewsets.ModelViewSet):
    queryset = RestaurantTable.objects.all().order_by('number')
    serializer_class = RestaurantTableSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [ServicePermission()]


class ReservationViewSet(viewsets.ModelViewSet):
    permission_classes = [ServicePermission]
    queryset = Reservation.objects.select_related('table').order_by('-reservation_at')
    serializer_class = ReservationSerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all().order_by('name')
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()] if self.request.query_params.get('public') == '1' else [ActiveStaffPermission()]
        return [OwnerManagerPermission()]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related(
        'details__menu_item'
    ).select_related('salesclerk', 'waiter', 'cashier', 'table').order_by('-created_at')
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [ActiveStaffPermission()]

    @action(detail=True, methods=['get'], permission_classes=[CashierManagerPermission])
    def receipt(self, request, pk=None):
        order = self.get_object()
        payments = list(order.payments.order_by('created_at'))
        paid_total = sum(p.amount for p in payments if p.status == 'paid')
        return Response({
            'receipt_number': f'SVR-{order.id:06d}',
            'order': OrderSerializer(order, context={'request': request}).data,
            'payments': PaymentSerializer(payments, many=True).data,
            'paid_total': paid_total,
            'balance': order.total - paid_total,
            'is_paid': paid_total >= order.total,
        })


class OrderDetailViewSet(viewsets.ModelViewSet):
    permission_classes = [KitchenPermission]
    queryset = OrderDetail.objects.select_related('order', 'menu_item').all()
    serializer_class = OrderDetailSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = [InventoryPermission]
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer


class ItemIngredientViewSet(viewsets.ModelViewSet):
    permission_classes = [InventoryPermission]
    queryset = ItemIngredient.objects.select_related(
        'menu_item', 'ingredient'
    ).all()
    serializer_class = ItemIngredientSerializer


class InventoryViewSet(viewsets.ModelViewSet):
    permission_classes = [InventoryPermission]
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
    permission_classes = [InventoryPermission]
    queryset = PurchaseOrder.objects.select_related(
        'ingredient'
    ).order_by('-created_at')
    serializer_class = PurchaseOrderSerializer

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def receive(self, request, pk=None):
        purchase_order = self.get_object()
        if purchase_order.status.lower() == 'received':
            return Response(
                {'detail': 'This purchase order has already been received.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity_received = float(
                request.data.get('quantity_received', purchase_order.quantity_ordered)
            )
        except (TypeError, ValueError):
            return Response(
                {'quantity_received': 'Enter a valid quantity.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity_received <= 0:
            return Response(
                {'quantity_received': 'Quantity received must be greater than zero.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        inventory, _ = Inventory.objects.select_for_update().get_or_create(
            ingredient=purchase_order.ingredient,
            defaults={'quantity_in_stock': 0}
        )
        inventory.quantity_in_stock += quantity_received
        inventory.save(update_fields=['quantity_in_stock'])

        invoice, _ = Invoice.objects.get_or_create(
            purchase_order=purchase_order,
            defaults={'quantity_received': quantity_received}
        )
        purchase_order.status = 'Received'
        purchase_order.save(update_fields=['status'])

        return Response({
            'purchase_order': PurchaseOrderSerializer(purchase_order).data,
            'invoice': InvoiceSerializer(invoice).data,
            'quantity_in_stock': inventory.quantity_in_stock,
        })


class InvoiceViewSet(viewsets.ModelViewSet):
    permission_classes = [InventoryPermission]
    queryset = Invoice.objects.select_related(
        'purchase_order__ingredient'
    ).order_by('-received_at')
    serializer_class = InvoiceSerializer


class ChequeViewSet(viewsets.ModelViewSet):
    permission_classes = [OwnerManagerPermission]
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
