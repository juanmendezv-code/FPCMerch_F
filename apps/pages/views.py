from django.db.models import Count, Q
from django.shortcuts import render
from apps.products.models import Category, Product

def home(request):
    categories = Category.objects.annotate(product_count=Count("products", filter=Q(products__is_active=True)))
    featured = Product.objects.filter(is_active=True, is_featured=True).select_related("category")[:8]
    return render(request, "home.html", {"categories": categories, "featured_products": featured})

def info_page(request, slug):
    pages = {"terminos": ("Términos y condiciones", "Contenido ilustrativo: reemplaza estas condiciones por los términos revisados para tu operación."), "devoluciones": ("Devoluciones y cambios", "Contenido ilustrativo: confirma aquí plazos, condiciones y canales para cambios."), "guia-de-tallas": ("Guía de tallas", "Contenido ilustrativo: verifica la tabla de medidas de cada fabricante antes de comprar."), "preguntas-frecuentes": ("Preguntas frecuentes", "Contenido ilustrativo: agrega respuestas confirmadas sobre envíos, tallas y pedidos."), "seguimiento": ("Seguimiento de pedido", "Inicia sesión para consultar tus pedidos. Esta página no consulta pedidos de otras cuentas.")}
    title, body = pages.get(slug, ("Página informativa", "Contenido ilustrativo."))
    if slug == "seguimiento" and request.user.is_authenticated:
        from apps.orders.models import Order
        orders = Order.objects.filter(user=request.user)
    else: orders = []
    return render(request, "pages/info.html", {"title": title, "body": body, "orders": orders})

def bad_request(request, exception): return render(request, "errors/400.html", status=400)
def permission_denied(request, exception): return render(request, "errors/403.html", status=403)
def page_not_found(request, exception): return render(request, "errors/404.html", status=404)
def server_error(request): return render(request, "errors/500.html", status=500)
