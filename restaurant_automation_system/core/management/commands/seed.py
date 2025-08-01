from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    MenuItem, Ingredient, Inventory, ItemIngredient
)

class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **kwargs):
        # Create Users
        manager, _ = User.objects.get_or_create(username='manager')
        manager.set_password('manager123')
        manager.is_staff = True
        manager.save()

        clerk, _ = User.objects.get_or_create(username='clerk')
        clerk.set_password('clerk123')
        clerk.save()

        self.stdout.write("✅ Created test users")

        # Ingredients
        ingredients = [
            {"name": "Tomato", "unit": "kg", "threshold": 5},
            {"name": "Cheese", "unit": "kg", "threshold": 3},
            {"name": "Flour", "unit": "kg", "threshold": 10},
            {"name": "Beef", "unit": "kg", "threshold": 4},
        ]

        for ing in ingredients:
            obj, _ = Ingredient.objects.get_or_create(
                name=ing["name"],
                unit=ing["unit"],
                threshold=ing["threshold"]
            )
            Inventory.objects.get_or_create(ingredient=obj, quantity_in_stock=20)

        self.stdout.write("✅ Created ingredients and inventory")

        # Menu Items
        pizza = MenuItem.objects.create(name="Beef Pizza", price=1200.00)
        burger = MenuItem.objects.create(name="Cheese Burger", price=800.00)

        # Map Ingredients to Menu Items
        ItemIngredient.objects.create(menu_item=pizza, ingredient=Ingredient.objects.get(name="Flour"), quantity_required=0.3)
        ItemIngredient.objects.create(menu_item=pizza, ingredient=Ingredient.objects.get(name="Beef"), quantity_required=0.4)
        ItemIngredient.objects.create(menu_item=pizza, ingredient=Ingredient.objects.get(name="Cheese"), quantity_required=0.2)

        ItemIngredient.objects.create(menu_item=burger, ingredient=Ingredient.objects.get(name="Beef"), quantity_required=0.25)
        ItemIngredient.objects.create(menu_item=burger, ingredient=Ingredient.objects.get(name="Tomato"), quantity_required=0.1)
        ItemIngredient.objects.create(menu_item=burger, ingredient=Ingredient.objects.get(name="Cheese"), quantity_required=0.15)

        self.stdout.write("✅ Created menu items and item-ingredient mappings")

        self.stdout.write(self.style.SUCCESS("🌱 Seeding complete!"))
