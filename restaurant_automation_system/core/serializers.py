from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    MenuItem, Order, OrderDetail, Ingredient, ItemIngredient,
    Inventory, PurchaseOrder, Invoice, Cheque, RestaurantTable, Reservation, Payment, StaffProfile, CashierShift, AuditLog, Wastage
)


class StaffProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    email = serializers.EmailField(source='user.email', required=False, allow_blank=True)

    class Meta:
        model = StaffProfile
        fields = ['id', 'user', 'username', 'first_name', 'last_name', 'email', 'phone', 'role', 'active']
        read_only_fields = ['user', 'username']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        username = self.initial_data.get('username', '').strip()
        password = self.initial_data.get('password', '')
        if not username:
            raise serializers.ValidationError({'username': 'Username is required.'})
        if not password:
            raise serializers.ValidationError({'password': 'Password is required.'})
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': 'This username is already in use.'})
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            email=user_data.get('email', '')
        )
        return StaffProfile.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        for field in ('first_name', 'last_name', 'email'):
            if field in user_data:
                setattr(instance.user, field, user_data[field])
        instance.user.save()
        return super().update(instance, validated_data)


class MenuItemSerializer(serializers.ModelSerializer):
    image_display_url = serializers.SerializerMethodField()

    def get_image_display_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return obj.image_url

    class Meta:
        model = MenuItem
        fields = '__all__'


class RestaurantTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantTable
        fields = '__all__'


class ReservationSerializer(serializers.ModelSerializer):
    table_number = serializers.ReadOnlyField(source='table.number')

    class Meta:
        model = Reservation
        fields = '__all__'


class OrderDetailSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.ReadOnlyField(source='menu_item.name')
    prep_station = serializers.ReadOnlyField(source='menu_item.prep_station')
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderDetail
        fields = ['id', 'menu_item', 'menu_item_name', 'prep_station', 'quantity', 'subtotal', 'notes', 'status']


class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, write_only=True, required=False)
    salesclerk_username = serializers.ReadOnlyField(source='salesclerk.username')
    salesclerk_name = serializers.SerializerMethodField()
    salesclerk_roles = serializers.SerializerMethodField()
    table_number = serializers.ReadOnlyField(source='table.number')
    waiter_name = serializers.SerializerMethodField()
    cashier_name = serializers.SerializerMethodField()
    details = OrderDetailSerializer(many=True, read_only=True)
    total = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'salesclerk', 'salesclerk_username', 'salesclerk_name',
            'salesclerk_roles', 'waiter', 'waiter_name', 'cashier', 'cashier_name',
            'table', 'table_number', 'order_type', 'status',
            'customer_name', 'customer_phone', 'notes', 'created_at',
            'updated_at', 'subtotal', 'discount_amount', 'service_charge_amount', 'tax_amount', 'tip_amount', 'adjustment_note', 'total', 'order_details', 'details'
        ]
        read_only_fields = ['salesclerk', 'created_at', 'updated_at', 'subtotal', 'discount_amount', 'service_charge_amount', 'tax_amount', 'tip_amount', 'adjustment_note', 'total']

    def get_salesclerk_name(self, obj):
        if not obj.salesclerk:
            return ''
        full_name = obj.salesclerk.get_full_name().strip()
        return full_name or obj.salesclerk.username

    def get_waiter_name(self, obj):
        if not obj.waiter:
            return ''
        return obj.waiter.get_full_name().strip() or obj.waiter.username

    def get_cashier_name(self, obj):
        if not obj.cashier:
            return ''
        return obj.cashier.get_full_name().strip() or obj.cashier.username

    def get_salesclerk_roles(self, obj):
        if not obj.salesclerk:
            return []
        return list(obj.salesclerk.groups.values_list('name', flat=True))

    @transaction.atomic
    def create(self, validated_data):
        order_details_data = validated_data.pop('order_details', [])
        request = self.context.get('request')
        salesclerk = (
            request.user
            if request and request.user and request.user.is_authenticated
            else None
        )
        if not order_details_data:
            raise serializers.ValidationError({'order_details': 'Add at least one item.'})

        if salesclerk:
            profile = getattr(salesclerk, 'staff_profile', None)
            if profile and profile.active:
                if profile.role == 'cashier' and not validated_data.get('cashier'):
                    validated_data['cashier'] = salesclerk
                if profile.role == 'waiter' and not validated_data.get('waiter'):
                    validated_data['waiter'] = salesclerk

        order = Order.objects.create(salesclerk=salesclerk, **validated_data)

        total = 0

        for detail_data in order_details_data:
            menu_item = detail_data['menu_item']
            quantity = detail_data['quantity']
            notes = detail_data.get('notes', '')

            if quantity <= 0:
                raise serializers.ValidationError(
                    {'order_details': 'Quantity must be greater than zero.'}
                )

            if not menu_item.available:
                raise serializers.ValidationError(
                    {'order_details': f'{menu_item.name} is currently unavailable.'}
                )

            subtotal = menu_item.price * quantity

            item_ingredients = ItemIngredient.objects.select_related(
                'ingredient'
            ).filter(menu_item=menu_item)

            inventory_updates = []
            for item_ingredient in item_ingredients:
                total_required = item_ingredient.quantity_required * quantity

                try:
                    inventory = Inventory.objects.select_for_update().get(
                        ingredient=item_ingredient.ingredient
                    )
                except Inventory.DoesNotExist:
                    raise serializers.ValidationError(
                        {
                            'order_details':
                            f'Inventory record missing for '
                            f'{item_ingredient.ingredient.name}.'
                        }
                    )

                if inventory.quantity_in_stock < total_required:
                    raise serializers.ValidationError(
                        {
                            'order_details':
                            f'Not enough stock for '
                            f'{item_ingredient.ingredient.name}.'
                        }
                    )

                inventory.quantity_in_stock -= total_required
                inventory_updates.append(inventory)

            OrderDetail.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                subtotal=subtotal,
                notes=notes
            )

            for inventory in inventory_updates:
                inventory.save(update_fields=['quantity_in_stock'])

            total += subtotal

        order.subtotal = total
        order.total = total
        order.save(update_fields=['subtotal', 'total'])

        if order.table:
            order.table.status = 'ordering'
            order.table.save(update_fields=['status', 'status_changed_at'])

        return order


class IngredientSerializer(serializers.ModelSerializer):
    threshold = serializers.ReadOnlyField(source='reorder_threshold')

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'unit', 'reorder_threshold', 'threshold', 'cost_per_unit']


class WastageSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.ReadOnlyField(source='ingredient.name')
    ingredient_unit = serializers.ReadOnlyField(source='ingredient.unit')
    recorded_by_name = serializers.ReadOnlyField(source='recorded_by.username')

    class Meta:
        model = Wastage
        fields = '__all__'
        read_only_fields = ['recorded_by']


class ItemIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemIngredient
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    ingredient_name = serializers.ReadOnlyField(source='ingredient.name')
    ingredient_unit = serializers.ReadOnlyField(source='ingredient.unit')
    threshold = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = [
            'id', 'ingredient', 'ingredient_name', 'ingredient_unit',
            'quantity_in_stock', 'threshold', 'is_low_stock'
        ]

    def get_threshold(self, obj):
        return obj.ingredient.calculate_threshold()

    def get_is_low_stock(self, obj):
        return obj.quantity_in_stock <= obj.ingredient.calculate_threshold()


class PurchaseOrderSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.ReadOnlyField(source='ingredient.name')
    ingredient_unit = serializers.ReadOnlyField(source='ingredient.unit')

    class Meta:
        model = PurchaseOrder
        fields = '__all__'

    def validate_status(self, value):
        normalized = str(value).strip().lower()
        mapping = {'pending': 'Pending', 'received': 'Received'}
        if normalized not in mapping:
            raise serializers.ValidationError('Use pending or received.')
        return mapping[normalized]


class InvoiceSerializer(serializers.ModelSerializer):
    purchase_order_info = serializers.StringRelatedField(
        source='purchase_order', read_only=True
    )

    class Meta:
        model = Invoice
        fields = [
            'id', 'purchase_order', 'purchase_order_info',
            'quantity_received', 'received_at'
        ]
        read_only_fields = ['received_at']


class ChequeSerializer(serializers.ModelSerializer):
    invoice_info = serializers.StringRelatedField(
        source='invoice', read_only=True
    )

    class Meta:
        model = Cheque
        fields = ['id', 'invoice', 'invoice_info', 'amount', 'issued_at']
        read_only_fields = ['issued_at']


class CashierShiftSerializer(serializers.ModelSerializer):
    cashier_name = serializers.SerializerMethodField()

    class Meta:
        model = CashierShift
        fields = '__all__'
        read_only_fields = [
            'cashier', 'expected_cash', 'variance', 'status',
            'opened_at', 'closed_at'
        ]

    def get_cashier_name(self, obj):
        return obj.cashier.get_full_name().strip() or obj.cashier.username


class PaymentSerializer(serializers.ModelSerializer):
    order_total = serializers.ReadOnlyField(source='order.total')
    order_table = serializers.ReadOnlyField(source='order.table.number')
    cashier_name = serializers.SerializerMethodField()
    processed_by_name = serializers.SerializerMethodField()

    def get_processed_by_name(self, obj):
        if not obj.processed_by:
            return ''
        return obj.processed_by.get_full_name().strip() or obj.processed_by.username

    def get_cashier_name(self, obj):
        cashier = getattr(obj.order, 'cashier', None)
        if not cashier:
            return ''
        return cashier.get_full_name().strip() or cashier.username

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['created_at', 'paid_at', 'status']

    @transaction.atomic
    def create(self, validated_data):
        from django.utils import timezone

        order = validated_data['order']
        amount = validated_data['amount']

        if amount <= 0:
            raise serializers.ValidationError({'amount': 'Payment must be greater than zero.'})

        paid_total = sum(
            payment.amount
            for payment in order.payments.filter(status='paid')
        )
        outstanding = order.total - paid_total
        if amount > outstanding:
            raise serializers.ValidationError(
                {'amount': f'Payment exceeds outstanding balance of {outstanding}.'}
            )

        method = validated_data.get('method')
        if method == 'mpesa':
            validated_data['status'] = 'pending'
        elif method in ('cash', 'card'):
            validated_data['status'] = 'paid'
            validated_data['paid_at'] = timezone.now()

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['processed_by'] = request.user

        payment = Payment.objects.create(**validated_data)

        paid_total += payment.amount if payment.status == 'paid' else 0
        if paid_total >= order.total:
            order.status = 'completed'
            order.save(update_fields=['status', 'updated_at'])
            if order.table:
                order.table.status = 'cleaning'
                order.table.save(update_fields=['status', 'status_changed_at'])
        else:
            order.status = 'awaiting_payment'
            order.save(update_fields=['status', 'updated_at'])

        return payment


class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()
    table_number = serializers.ReadOnlyField(source='order.table.number')

    class Meta:
        model = AuditLog
        fields = '__all__'

    def get_actor_name(self, obj):
        if not obj.actor:
            return 'System'
        return obj.actor.get_full_name().strip() or obj.actor.username
