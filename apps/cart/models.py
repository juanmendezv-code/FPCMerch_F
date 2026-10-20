from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from apps.products.models import ProductSize

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"Carrito de {self.user}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductSize, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    class Meta:
        constraints = [models.UniqueConstraint(fields=("cart", "variant"), name="unique_cart_variant"), models.CheckConstraint(condition=Q(quantity__gte=1), name="cart_item_quantity_positive")]
    def __str__(self): return f"{self.variant} × {self.quantity}"
