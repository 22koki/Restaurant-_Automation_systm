from rest_framework import serializers
from django.db import transaction
from .models import (
    MenuItem, Order, OrderDetail, Ingredient, ItemIngredient,
    Inventory, PurchaseOrder, Invoice, Cheque
)


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'


class OrderDetailSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.ReadOnlyField(source='menu_item.name')

    class Meta:
        model = OrderDetail
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, write_only=True)
    details = OrderDetailSerializer(source='orderdetail_set', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'salesclerk', 'created_at', 'total', 'order_details', 'details']

    @transaction.atomic
    def create(self, validated_data):
        order_details_data = validated_data.pop('order_details')
        order = Order.objects.create(**validated_data)

        total = 0

        for detail_data in order_details_data:
            menu_item = detail_data['menu_item']
            quantity = detail_data['quantity']
            subtotal = menu_item.price * quantity

            OrderDetail.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                subtotal=subtotal
            )

            total += subtotal

            # Deduct ingredients from inventory
            item_ingredients = ItemIngredient.objects.filter(menu_item=menu_item)
            for item_ingredient in item_ingredients:
                total_required = item_ingredient.quantity_required * quantity

                try:
                    inventory = Inventory.objects.get(ingredient=item_ingredient.ingredient)
                    if inventory.quantity_in_stock < total_required:
                        raise serializers.ValidationError(
                            f"Not enough stock for {item_ingredient.ingredient.name}."
                        )
                    inventory.quantity_in_stock -= total_required
                    inventory.save()
                except Inventory.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Inventory record missing for ingredient {item_ingredient.ingredient.name}."
                    )

        order.total = total
        order.save()
        return order


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class ItemIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemIngredient
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    ingredient_name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = Inventory
        fields = ['id', 'ingredient', 'ingredient_name', 'quantity_in_stock', 'threshold']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = PurchaseOrder
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    purchase_order_info = serializers.StringRelatedField(source='purchase_order', read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'purchase_order', 'purchase_order_info', 'quantity_received', 'price_per_unit', 'date']


class ChequeSerializer(serializers.ModelSerializer):
    invoice_info = serializers.StringRelatedField(source='invoice', read_only=True)

    class Meta:
        model = Cheque
        fields = ['id', 'invoice', 'invoice_info', 'amount', 'issued_date']
