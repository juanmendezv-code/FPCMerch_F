import json
from functools import wraps
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from apps.cart.services import InvalidQuantityError, OutOfStockError, add_item, cart_data, remove_item, update_item
from apps.products.models import Category, Product, ProductSize
from apps.products.services import filtered_products

def error(message, code, status=400):
    return JsonResponse({"ok": False, "error": message, "code": code}, status=status)

def csrf_failure(request, reason=""):
    if request.path.startswith("/api/"):
        return error("La verificación de seguridad falló. Recarga la página e inténtalo de nuevo.", "csrf_failed", 403)
    from django.shortcuts import render
    return render(request, "errors/403.html", status=403)

def json_method(method):
    def decorate(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.method != method:
                return error("Método HTTP no permitido.", "method_not_allowed", 405)
            return view(request, *args, **kwargs)
        return wrapped
    return decorate

def product_json(product):
    return {
        "id": product.pk,
        "name": product.name,
        "slug": product.slug,
        "sku": product.sku,
        "price": str(product.price),
        "currency": "COP",
        "category": product.category.name,
        "category_slug": product.category.slug,
        "stock": product.stock_total,
        "is_featured": product.is_featured,
        "url": f"/producto/{product.slug}/",
        "image": product.image.url if product.image else "",
    }

@json_method("GET")
def products_api(request):
    page = Paginator(filtered_products(request.GET), 12).get_page(request.GET.get("page"))
    return JsonResponse({"ok": True, "count": page.paginator.count, "page": page.number, "pages": page.paginator.num_pages, "results": [product_json(p) for p in page.object_list]})

@json_method("GET")
def product_detail_api(request, slug):
    product = Product.objects.prefetch_related("sizes").filter(slug=slug, is_active=True).first()
    if product is None:
        return error("Producto no encontrado.", "not_found", 404)
    data = product_json(product)
    data["description"] = product.description
    data["sizes"] = [{"id": v.pk, "size": v.size, "stock": v.stock} for v in product.sizes.all()]
    return JsonResponse({"ok": True, "product": data})

@json_method("GET")
def search_api(request):
    query = (request.GET.get("q") or "").strip()
    if len(query) < 2: return JsonResponse({"ok": True, "results": []})
    return JsonResponse({"ok": True, "results": [product_json(p) for p in filtered_products({"q": query})[:6]]})

@json_method("GET")
def categories_api(request):
    categories = Category.objects.annotate(product_count=Count("products", filter=Q(products__is_active=True)))
    return JsonResponse({"ok": True, "results": [{"name": c.name, "slug": c.slug, "count": c.product_count} for c in categories]})

def cart_json(request):
    data = cart_data(request)
    return JsonResponse({"ok": True, "count": data["count"], "total": str(data["total"]), "items": [{"product": l["product"].name, "size": l["size"], "quantity": l["quantity"], "price": str(l["product"].price), "subtotal": str(l["subtotal"]), "variant_id": l["variant"].pk} for l in data["lines"]]})

@json_method("GET")
def cart_api(request): return cart_json(request)

def payload(request):
    try: return json.loads(request.body or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError): raise ValueError("El cuerpo JSON no es válido.")

@json_method("POST")
def cart_add_api(request):
    try:
        data = payload(request)
        add_item(request, int(data["product_id"]), int(data["size_id"]), int(data.get("quantity", 1)))
    except ValueError as exc: return error(str(exc) or "Cantidad inválida.", "invalid_quantity")
    except KeyError: return error("Faltan campos requeridos.", "invalid_request")
    except OutOfStockError as exc: return error(str(exc), "out_of_stock")
    except InvalidQuantityError as exc: return error(str(exc), "invalid_quantity")
    except (Product.DoesNotExist, ProductSize.DoesNotExist): return error("Producto o talla no disponible.", "not_found", 404)
    return cart_json(request)

@json_method("POST")
def cart_update_api(request):
    try:
        data = payload(request)
        update_item(request, int(data["size_id"]), int(data["quantity"]))
    except (ValueError, KeyError) as exc: return error(str(exc) or "Cantidad o talla inválida.", "invalid_quantity")
    except OutOfStockError as exc: return error(str(exc), "out_of_stock")
    except InvalidQuantityError as exc: return error(str(exc), "invalid_quantity")
    except ProductSize.DoesNotExist: return error("La talla no está disponible.", "not_found", 404)
    return cart_json(request)

@json_method("POST")
def cart_remove_api(request):
    try:
        data = payload(request)
        remove_item(request, int(data["size_id"]))
    except (ValueError, KeyError) as exc: return error(str(exc) or "Talla inválida.", "invalid_request")
    return cart_json(request)
