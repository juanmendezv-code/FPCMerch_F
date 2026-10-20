from django.contrib import admin
from .models import Category, Product, ProductSize

class ProductSizeInline(admin.TabularInline):
    model = ProductSize; extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order"); prepopulated_fields = {"slug": ("name",)}; search_fields = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "is_active", "is_featured", "updated_at")
    list_filter = ("category", "is_active", "is_featured"); search_fields = ("name", "sku", "description")
    prepopulated_fields = {"slug": ("name",)}; list_editable = ("price", "is_active", "is_featured"); inlines = (ProductSizeInline,)
