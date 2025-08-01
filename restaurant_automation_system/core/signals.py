from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import OrderDetail, Inventory, ItemIngredient, PurchaseOrder


@receiver(post_save, sender=OrderDetail)
def update_inventory_on_order(sender, instance, created, **kwargs):
    if not created:
        return  # Only run on new OrderDetail creation

    menu_item = instance.menu_item
    quantity_ordered = instance.quantity

    item_ingredients = ItemIngredient.objects.filter(menu_item=menu_item)

    for item_ingredient in item_ingredients:
        try:
            inventory_item = Inventory.objects.get(ingredient=item_ingredient.ingredient)
            required_amount = item_ingredient.quantity_required * quantity_ordered
            inventory_item.quantity_in_stock -= required_amount
            inventory_item.save()

            # Trigger reorder if stock falls below threshold
            if inventory_item.quantity_in_stock <= item_ingredient.ingredient.threshold:
                existing_po = PurchaseOrder.objects.filter(
                    ingredient=inventory_item.ingredient,
                    status="Pending"
                ).exists()

                if not existing_po:
                    PurchaseOrder.objects.create(
                        ingredient=inventory_item.ingredient,
                        quantity_ordered=item_ingredient.ingredient.threshold * 2,  # adjustable logic
                        date_ordered=timezone.now(),
                        status="Pending"
                    )
        except Inventory.DoesNotExist:
            # Optional: log this event
            pass
