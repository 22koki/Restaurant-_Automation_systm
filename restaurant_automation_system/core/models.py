from django.contrib.auth.models import User
from django.db import models


class StaffProfile(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
        ('waiter', 'Waiter'),
        ('kitchen', 'Kitchen'),
        ('storekeeper', 'Storekeeper'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=40, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} - {self.role}'


class MenuItem(models.Model):
    STATION_CHOICES = [
        ('kitchen', 'Kitchen'),
        ('grill', 'Grill'),
        ('bar', 'Bar'),
        ('dessert', 'Dessert'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=80, default='Mains')
    image_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    prep_station = models.CharField(
        max_length=20,
        choices=STATION_CHOICES,
        default='kitchen'
    )

    def __str__(self):
        return self.name


class RestaurantTable(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
        ('ordering', 'Ordering'),
        ('preparing', 'Preparing'),
        ('ready_to_bill', 'Ready to bill'),
        ('cleaning', 'Cleaning'),
    ]

    number = models.CharField(max_length=20, unique=True)
    seats = models.PositiveIntegerField(default=2)
    area = models.CharField(max_length=80, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    active = models.BooleanField(default=True)
    status_changed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Table {self.number}'


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('seated', 'Seated'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No show'),
    ]

    customer_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    party_size = models.PositiveIntegerField()
    reservation_at = models.DateTimeField()
    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations'
    )
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer_name} - {self.reservation_at:%Y-%m-%d %H:%M}'


class Order(models.Model):
    TYPE_CHOICES = [
        ('dine_in', 'Dine in'),
        ('takeaway', 'Takeaway'),
        ('delivery', 'Delivery'),
        ('online', 'Online'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('awaiting_payment', 'Awaiting payment'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    salesclerk = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    waiter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='waiter_orders'
    )
    cashier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cashier_orders'
    )
    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    order_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='dine_in'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed'
    )
    customer_name = models.CharField(max_length=120, blank=True)
    customer_phone = models.CharField(max_length=40, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    service_charge_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tip_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    adjustment_note = models.CharField(max_length=255, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'Order #{self.id} - {self.created_at}'


class OrderDetail(models.Model):
    ITEM_STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.ForeignKey(
        Order,
        related_name='details',
        on_delete=models.CASCADE
    )
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ITEM_STATUS_CHOICES,
        default='queued'
    )

    def __str__(self):
        return f'{self.quantity} x {self.menu_item.name}'


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)
    reorder_threshold = models.FloatField(default=5.0)

    def calculate_threshold(self):
        return self.reorder_threshold


class IngredientUsage(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_used = models.FloatField()
    used_at = models.DateTimeField(auto_now_add=True)


class ItemIngredient(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_required = models.FloatField(
        help_text='Quantity needed per menu item'
    )

    def __str__(self):
        return (
            f'{self.quantity_required} of {self.ingredient.name} '
            f'for {self.menu_item.name}'
        )


class Inventory(models.Model):
    ingredient = models.OneToOneField(Ingredient, on_delete=models.CASCADE)
    quantity_in_stock = models.FloatField()

    def __str__(self):
        return f'{self.ingredient.name}: {self.quantity_in_stock} in stock'


class PurchaseOrder(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_ordered = models.FloatField()
    status = models.CharField(
        max_length=10,
        choices=[('Pending', 'Pending'), ('Received', 'Received')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'PO: {self.ingredient.name} '
            f'({self.quantity_ordered}) - {self.status}'
        )


class Invoice(models.Model):
    purchase_order = models.OneToOneField(
        PurchaseOrder,
        on_delete=models.CASCADE
    )
    quantity_received = models.FloatField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Invoice for {self.purchase_order.ingredient.name}'


class Cheque(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cheque for Invoice #{self.invoice.id}'


class CashRegister(models.Model):
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cash Balance: {self.balance}'


class PriceChangeLog(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    old_price = models.DecimalField(max_digits=8, decimal_places=2)
    new_price = models.DecimalField(max_digits=8, decimal_places=2)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'{self.menu_item.name}: {self.old_price} -> '
            f'{self.new_price} on {self.changed_at}'
        )


class SalesReport(models.Model):
    month = models.DateField(help_text='Any date within the month')
    total_sales = models.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.month.strftime('%B %Y')}"


class CashBalance(models.Model):
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cash Balance: {self.balance}'


class CashierShift(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    cashier = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='cashier_shifts'
    )
    opening_float = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    counted_cash = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expected_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    variance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.cashier.username} shift #{self.id} - {self.status}'


class Payment(models.Model):
    METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
        ('card', 'Card'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    reference = models.CharField(max_length=120, blank=True)
    phone_number = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payments'
    )
    refund_reason = models.CharField(max_length=255, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    refunded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refunded_payments'
    )

    def __str__(self):
        return f'Payment #{self.id} for Order #{self.order_id}'
