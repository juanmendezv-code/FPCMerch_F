from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "size", "quantity", "unit_price")
    def has_add_permission(self, request, obj=None): return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "user", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("number", "user__email")
    list_editable = ("status",)
    inlines = (OrderItemInline,)
