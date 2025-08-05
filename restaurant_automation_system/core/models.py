from django.db import models
from django.contrib.auth.models import User


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    salesclerk = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order #{self.id} - {self.created_at}"


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name='details', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)

    def calculate_threshold(self):
        from datetime import timedelta
        from django.utils import timezone

        three_days_ago = timezone.now() - timedelta(days=3)
        usages = IngredientUsage.objects.filter(ingredient=self, used_at__gte=three_days_ago)
        total_used = sum(u.quantity_used for u in usages)
        avg_per_day = total_used / 3 if total_used else 0
        return avg_per_day * 2
 # NEW
class IngredientUsage(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_used = models.FloatField()
    used_at = models.DateTimeField(auto_now_add=True)
     

class ItemIngredient(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_required = models.FloatField(help_text="Quantity needed per menu item")

    def __str__(self):
        return f"{self.quantity_required} of {self.ingredient.name} for {self.menu_item.name}"


class Inventory(models.Model):
    ingredient = models.OneToOneField(Ingredient, on_delete=models.CASCADE)
    quantity_in_stock = models.FloatField()

    def __str__(self):
        return f"{self.ingredient.name}: {self.quantity_in_stock} in stock"


class PurchaseOrder(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_ordered = models.FloatField()
    status = models.CharField(
        max_length=10,
        choices=[("Pending", "Pending"), ("Received", "Received")],
        default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PO: {self.ingredient.name} ({self.quantity_ordered}) - {self.status}"


class Invoice(models.Model):
    purchase_order = models.OneToOneField(PurchaseOrder, on_delete=models.CASCADE)
    quantity_received = models.FloatField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice for {self.purchase_order.ingredient.name}"


class Cheque(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cheque for Invoice #{self.invoice.id}"
class CashRegister(models.Model):
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cash Balance: {self.balance}"
class PriceChangeLog(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    old_price = models.DecimalField(max_digits=8, decimal_places=2)
    new_price = models.DecimalField(max_digits=8, decimal_places=2)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.menu_item.name}: {self.old_price} → {self.new_price} on {self.changed_at}"
class SalesReport(models.Model):
    month = models.DateField(help_text="Any date within the month")
    total_sales = models.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.month.strftime('%B %Y')}"
class CashBalance(models.Model):
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cash Balance: {self.balance}"
