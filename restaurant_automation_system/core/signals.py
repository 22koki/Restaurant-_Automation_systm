from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import OrderDetail, Inventory, ItemIngredient, PurchaseOrder


@receiver(post_save, sender=OrderDetail)
def update_inventory_on_order(sender, instance, created, **kwargs):
    if not created:
        return

    menu_item = instance.menu_item
    quantity_ordered = instance.quantity

    item_ingredients = ItemIngredient.objects.filter(menu_item=menu_item)

    for item_ingredient in item_ingredients:
        ingredient = item_ingredient.ingredient
        required_amount = item_ingredient.quantity_required * quantity_ordered

        try:
            inventory_item = Inventory.objects.get(ingredient=ingredient)
        except Inventory.DoesNotExist:
            print(f"Inventory record not found for ingredient: {ingredient.name}")
            continue

        # Deduct used ingredients
        inventory_item.quantity_in_stock -= required_amount
        inventory_item.save()

        # Calculate average usage for last 3 days
        last_3_days = timezone.now() - timedelta(days=3)
        recent_usages = OrderDetail.objects.filter(
            created_at__gte=last_3_days,
            menu_item__itemingredient__ingredient=ingredient
        )

        total_consumed = 0
        for usage in recent_usages:
            related_ingredients = ItemIngredient.objects.filter(menu_item=usage.menu_item, ingredient=ingredient)
            for rel in related_ingredients:
                total_consumed += usage.quantity * rel.quantity_required

        average_daily_usage = total_consumed / 3

        # Reorder if current stock is below or equal to average usage
        if inventory_item.quantity_in_stock <= average_daily_usage:
            already_pending = PurchaseOrder.objects.filter(
                ingredient=ingredient,
                status="Pending"
            ).exists()

            if not already_pending:
                reorder_qty = average_daily_usage * 3  # stock for next 3 days
                PurchaseOrder.objects.create(
                    ingredient=ingredient,
                    quantity_ordered=reorder_qty,
                    status="Pending"
                )
