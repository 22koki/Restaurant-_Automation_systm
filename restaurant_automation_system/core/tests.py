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
    Order, StaffProfile,
)


class OrderApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='cashier',
            password='test-password'
        )
        StaffProfile.objects.create(user=self.user, role='cashier')
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
    def setUp(self):
        user = User.objects.create_user(username='storekeeper', password='test-password')
        StaffProfile.objects.create(user=user, role='storekeeper')
        self.client.force_authenticate(user=user)

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
        user = User.objects.create_user(username='kitchen', password='test-password')
        StaffProfile.objects.create(user=user, role='kitchen')
        self.client.force_authenticate(user=user)
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
        user = User.objects.create_user(username='waiter', password='test-password')
        StaffProfile.objects.create(user=user, role='waiter')
        self.client.force_authenticate(user=user)
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


class PaymentWorkflowTests(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username='payment-cashier', password='test-password')
        StaffProfile.objects.create(user=user, role='cashier')
        self.client.force_authenticate(user=user)
        from .models import RestaurantTable
        self.table = RestaurantTable.objects.create(number='12', seats=4, status='ready_to_bill')
        self.order = Order.objects.create(
            table=self.table,
            order_type='dine_in',
            status='awaiting_payment',
            total=Decimal('2000.00')
        )

    def test_cash_payment_completes_order_and_sends_table_to_cleaning(self):
        response = self.client.post(
            reverse('payment-list'),
            {'order': self.order.id, 'method': 'cash', 'amount': '2000.00'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.order.refresh_from_db()
        self.table.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')
        self.assertEqual(self.table.status, 'cleaning')
        self.assertEqual(response.data['status'], 'paid')

    def test_partial_payment_keeps_order_awaiting_payment(self):
        response = self.client.post(
            reverse('payment-list'),
            {'order': self.order.id, 'method': 'cash', 'amount': '500.00'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'awaiting_payment')

    def test_overpayment_is_rejected(self):
        response = self.client.post(
            reverse('payment-list'),
            {'order': self.order.id, 'method': 'card', 'amount': '2500.00'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
