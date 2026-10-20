from django.db.models import Q
from .models import Product

def filtered_products(params):
    products = Product.objects.filter(is_active=True).select_related("category").prefetch_related("sizes")
    query = (params.get("q") or "").strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(sku__icontains=query) | Q(category__name__icontains=query))
    category = params.get("categoria")
    if category: products = products.filter(category__slug=category)
    price_max = params.get("precio_max")
    if price_max:
        try: products = products.filter(price__lte=max(0, int(price_max)))
        except (TypeError, ValueError): pass
    size = params.get("talla")
    if size: products = products.filter(sizes__size__iexact=size, sizes__stock__gt=0).distinct()
    ordering = {"precio-asc": "price", "precio-desc": "-price", "nombre": "name", "nuevos": "-created_at"}.get(params.get("orden"), "-is_featured")
    return products.order_by(ordering, "name")
