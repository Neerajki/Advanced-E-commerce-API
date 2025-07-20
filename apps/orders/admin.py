from django.contrib import admin
from .models import Order, OrderItem


# Inline for Order Items
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity')
    can_delete = False


# Admin for Orders
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'user__email')
    inlines = [OrderItemInline]

    # Make status editable from list view
    list_editable = ('status',)

    # Optional: Readonly fields
    readonly_fields = ('total_price', 'created_at', 'updated_at')

    # Order by latest
    ordering = ('-created_at',)
