from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    IngredientUsage,
    Inventory,
    ItemIngredient,
    OrderDetail,
    PurchaseOrder,
)


@receiver(post_save, sender=OrderDetail)
def track_usage_and_reorder(sender, instance, created, **kwargs):
    if not created:
        return

    item_ingredients = ItemIngredient.objects.select_related(
        'ingredient'
    ).filter(menu_item=instance.menu_item)

    for item_ingredient in item_ingredients:
        ingredient = item_ingredient.ingredient
        quantity_used = item_ingredient.quantity_required * instance.quantity

        IngredientUsage.objects.create(
            ingredient=ingredient,
            quantity_used=quantity_used,
        )

        try:
            inventory_item = Inventory.objects.get(ingredient=ingredient)
        except Inventory.DoesNotExist:
            continue

        last_3_days = timezone.now() - timedelta(days=3)
        recent_usages = IngredientUsage.objects.filter(
            ingredient=ingredient,
            used_at__gte=last_3_days,
        )

        total_consumed = sum(
            usage.quantity_used for usage in recent_usages
        )
        average_daily_usage = total_consumed / 3 if total_consumed else 0

        if (
            average_daily_usage > 0
            and inventory_item.quantity_in_stock <= average_daily_usage
        ):
            already_pending = PurchaseOrder.objects.filter(
                ingredient=ingredient,
                status='Pending',
            ).exists()

            if not already_pending:
                PurchaseOrder.objects.create(
                    ingredient=ingredient,
                    quantity_ordered=average_daily_usage * 3,
                    status='Pending',
                )
