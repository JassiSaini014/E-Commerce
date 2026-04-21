from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User

admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)

class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0

    #extend Order model
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields =["date_order"]
    inlines = [OrderItemInline]

admin.site.unregister(Order)
admin.site.register(Order, OrderAdmin)
