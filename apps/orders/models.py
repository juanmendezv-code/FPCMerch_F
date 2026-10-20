from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from apps.products.models import Product

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        PAID = "paid", "Pagado (demo)"
        SHIPPED = "shipped", "Enviado"
        DELIVERED = "delivered", "Entregado"
        CANCELLED = "cancelled", "Cancelado"
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    number = models.CharField(max_length=24, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    shipping_address = models.CharField(max_length=240)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    payment_method = models.CharField(max_length=40, default="demo")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("user", "-created_at")), models.Index(fields=("number",))]
    def __str__(self): return self.number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    size = models.CharField(max_length=12, default="ÚNICA")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(quantity__gte=1), name="order_item_quantity_positive")]
    def __str__(self): return f"{self.product} × {self.quantity}"
