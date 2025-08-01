from rest_framework import serializers
from .models import (
    MenuItem, Order, OrderDetail, Ingredient, ItemIngredient,
    Inventory, PurchaseOrder, Invoice, Cheque
)


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['id', 'menu_item', 'quantity']
class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, write_only=True)
    details = OrderDetailSerializer(source='orderdetail_set', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'salesclerk', 'created_at', 'total', 'order_details', 'details']

    def create(self, validated_data):
        order_details_data = validated_data.pop('order_details')
        order = Order.objects.create(**validated_data)

        total = 0
        for detail_data in order_details_data:
            menu_item = detail_data['menu_item']
            quantity = detail_data['quantity']
            subtotal = menu_item.price * quantity

            # Now include subtotal when creating the OrderDetail
            OrderDetail.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                subtotal=subtotal
            )

            total += subtotal

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
    class Meta:
        model = Inventory
        fields = '__all__'


class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'


class ChequeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cheque
        fields = '__all__'
