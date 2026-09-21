from django.db import transaction
from rest_framework import serializers

from .models import (
    MenuItem, Order, OrderDetail, Ingredient, ItemIngredient,
    Inventory, PurchaseOrder, Invoice, Cheque, RestaurantTable, Reservation, Payment
)


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
    details = OrderDetailSerializer(many=True, read_only=True)
    total = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'salesclerk', 'salesclerk_username', 'salesclerk_name',
            'salesclerk_roles', 'table', 'table_number', 'order_type', 'status',
            'customer_name', 'customer_phone', 'notes', 'created_at',
            'updated_at', 'total', 'order_details', 'details'
        ]
        read_only_fields = ['salesclerk', 'created_at', 'updated_at', 'total']

    def get_salesclerk_name(self, obj):
        if not obj.salesclerk:
            return ''
        full_name = obj.salesclerk.get_full_name().strip()
        return full_name or obj.salesclerk.username

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

        order.total = total
        order.save(update_fields=['total'])
        return order


class IngredientSerializer(serializers.ModelSerializer):
    threshold = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'unit', 'threshold']

    def get_threshold(self, obj):
        return obj.calculate_threshold()


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

    class Meta:
        model = PurchaseOrder
        fields = '__all__'


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


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['created_at', 'paid_at']

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

        if validated_data.get('method') in ('cash', 'card'):
            validated_data['status'] = 'paid'
            validated_data['paid_at'] = timezone.now()

        payment = Payment.objects.create(**validated_data)

        paid_total += payment.amount if payment.status == 'paid' else 0
        if paid_total >= order.total:
            order.status = 'completed'
            order.save(update_fields=['status', 'updated_at'])
            if order.table:
                order.table.status = 'cleaning'
                order.table.save(update_fields=['status'])
        else:
            order.status = 'awaiting_payment'
            order.save(update_fields=['status', 'updated_at'])

        return payment
