from django.contrib import admin
from .models import Order, OrderItem, Product, Category

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'subtotal')
    can_delete = False

    def subtotal(self, obj):
        return obj.subtotal()
    subtotal.short_description = 'Subtotal'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total', 'status', 'ordered_at', 'delivery_location', 'notify_phone')
    list_filter = ('status', 'ordered_at')
    search_fields = ('customer__username', 'id')
    inlines = [OrderItemInline]
    ordering = ('-ordered_at',)
    list_editable=("status",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

