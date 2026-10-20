from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=40, default="⚽")
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ("order", "name")
        verbose_name_plural = "categories"
    def __str__(self): return self.name

class Product(models.Model):
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    sku = models.CharField(max_length=40, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    image = models.ImageField(upload_to="products/", blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("category", "is_active")), models.Index(fields=("name",)), models.Index(fields=("-created_at",))]
        constraints = [models.CheckConstraint(condition=Q(price__gte=0), name="product_price_nonnegative")]
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "producto"
            slug = base; suffix = 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{suffix}"; suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self): return self.name
    @property
    def stock_total(self): return sum(v.stock for v in self.sizes.all())

class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sizes")
    size = models.CharField(max_length=12, default="ÚNICA")
    stock = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ("size",)
        constraints = [models.UniqueConstraint(fields=("product", "size"), name="unique_product_size"), models.CheckConstraint(condition=Q(stock__gte=0), name="product_size_stock_nonnegative")]
    def __str__(self): return f"{self.product} · {self.size} ({self.stock})"
