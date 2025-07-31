from django.contrib import admin
from .models import (
    MenuItem, Order, OrderDetail, Ingredient,
    ItemIngredient, Inventory, PurchaseOrder,
    Invoice, Cheque
)

admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Ingredient)
admin.site.register(ItemIngredient)
admin.site.register(Inventory)
admin.site.register(PurchaseOrder)
admin.site.register(Invoice)
admin.site.register(Cheque)
