from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Ingredient,
    Inventory,
    ItemIngredient,
    MenuItem,
    Order,
)


class OrderApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='cashier',
            password='test-password'
        )
        self.client.force_authenticate(user=self.user)

        self.beef = Ingredient.objects.create(name='Beef', unit='g')
        self.beef_inventory = Inventory.objects.create(
            ingredient=self.beef,
            quantity_in_stock=1000
        )
        self.burger = MenuItem.objects.create(
            name='Beef Burger',
            price=Decimal('1200.00'),
            available=True
        )
        ItemIngredient.objects.create(
            menu_item=self.burger,
            ingredient=self.beef,
            quantity_required=180
        )

    def test_creating_order_calculates_total_and_deducts_inventory(self):
        response = self.client.post(
            reverse('order-list'),
            {
                'order_details': [
                    {'menu_item': self.burger.id, 'quantity': 2}
                ]
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(pk=response.data['id'])
        self.assertEqual(order.total, Decimal('2400.00'))
        self.assertEqual(order.salesclerk, self.user)

        self.beef_inventory.refresh_from_db()
        self.assertEqual(self.beef_inventory.quantity_in_stock, 640)
        from .models import IngredientUsage
        usage = IngredientUsage.objects.get(ingredient=self.beef)
        self.assertEqual(usage.quantity_used, 360)

    def test_order_rolls_back_when_stock_is_insufficient(self):
        response = self.client.post(
            reverse('order-list'),
            {
                'order_details': [
                    {'menu_item': self.burger.id, 'quantity': 10}
                ]
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

        self.beef_inventory.refresh_from_db()
        self.assertEqual(self.beef_inventory.quantity_in_stock, 1000)

    def test_unavailable_menu_item_cannot_be_ordered(self):
        self.burger.available = False
        self.burger.save(update_fields=['available'])

        response = self.client.post(
            reverse('order-list'),
            {
                'order_details': [
                    {'menu_item': self.burger.id, 'quantity': 1}
                ]
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)


class InventoryApiTests(APITestCase):
    def test_low_stock_endpoint_returns_dynamic_threshold_data(self):
        ingredient = Ingredient.objects.create(name='Tomatoes', unit='kg')
        inventory = Inventory.objects.create(
            ingredient=ingredient,
            quantity_in_stock=0
        )

        response = self.client.get('/api/low-stock/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = [item['id'] for item in response.data]
        self.assertIn(inventory.id, returned_ids)
        self.assertIn('threshold', response.data[0])
        self.assertIn('is_low_stock', response.data[0])


class RestaurantWorkflowTests(APITestCase):
    def setUp(self):
        self.menu_item = MenuItem.objects.create(
            name='Grilled Chicken',
            price=Decimal('1450.00'),
            available=True
        )

    def test_guest_can_place_takeaway_order_without_login(self):
        response = self.client.post(
            reverse('order-list'),
            {
                'order_type': 'takeaway',
                'customer_name': 'Guest',
                'order_details': [
                    {'menu_item': self.menu_item.id, 'quantity': 1}
                ]
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'confirmed')
        self.assertEqual(response.data['order_type'], 'takeaway')

    def test_kitchen_can_patch_item_status_without_order_payload(self):
        order = Order.objects.create(
            order_type='takeaway',
            status='confirmed',
            total=Decimal('1450.00')
        )
        from .models import OrderDetail
        detail = OrderDetail.objects.create(
            order=order,
            menu_item=self.menu_item,
            quantity=1,
            subtotal=Decimal('1450.00')
        )

        response = self.client.patch(
            reverse('orderdetail-detail', args=[detail.id]),
            {'status': 'preparing'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        detail.refresh_from_db()
        self.assertEqual(detail.status, 'preparing')

    def test_order_status_can_be_patched_without_resending_items(self):
        order = Order.objects.create(
            order_type='takeaway',
            status='confirmed',
            total=Decimal('1450.00')
        )

        response = self.client.patch(
            reverse('order-detail', args=[order.id]),
            {'status': 'served'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'served')
