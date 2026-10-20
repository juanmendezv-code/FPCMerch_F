from decimal import Decimal
from django.db import transaction
from django.db.models import F
from apps.products.models import Product, ProductSize
from .models import Cart, CartItem

CART_KEY = "fpcmerch_cart"

class InvalidQuantityError(Exception): pass
class OutOfStockError(Exception): pass
class EmptyCartError(Exception): pass

def cart_data(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        rows = CartItem.objects.filter(cart=cart, variant__product__is_active=True).select_related("variant__product", "variant__product__category")
        lines = [{"variant": row.variant, "product": row.variant.product, "size": row.variant.size, "quantity": row.quantity, "subtotal": row.variant.product.price * row.quantity} for row in rows]
        return {"lines": lines, "total": sum((line["subtotal"] for line in lines), Decimal("0")), "count": sum(line["quantity"] for line in lines)}
    raw = request.session.get(CART_KEY, {})
    lines = []; total = Decimal("0"); count = 0
    for key, quantity in raw.items():
        try:
            size_id = int(key); quantity = int(quantity)
            variant = ProductSize.objects.select_related("product", "product__category").get(pk=size_id, product__is_active=True)
        except (ValueError, TypeError, ProductSize.DoesNotExist): continue
        if quantity < 1: continue
        subtotal = variant.product.price * quantity
        lines.append({"variant": variant, "product": variant.product, "size": variant.size, "quantity": quantity, "subtotal": subtotal})
        total += subtotal; count += quantity
    return {"lines": lines, "total": total, "count": count}

def add_item(request, product_id, size_id, quantity):
    if not isinstance(quantity, int) or quantity < 1: raise InvalidQuantityError("La cantidad debe ser un entero mayor que cero.")
    product = Product.objects.get(pk=product_id, is_active=True)
    variant = ProductSize.objects.get(pk=size_id, product=product)
    if quantity > variant.stock: raise OutOfStockError("No hay existencias suficientes para esa cantidad.")
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, variant=variant, defaults={"quantity": 1})
        if created and quantity == 1: return
        if created: CartItem.objects.filter(pk=item.pk).update(quantity=quantity)
        else:
            changed = CartItem.objects.filter(pk=item.pk, quantity__lte=variant.stock - quantity).update(quantity=F("quantity") + quantity)
            if not changed:
                raise OutOfStockError("No hay existencias suficientes para esa cantidad.")
        item.refresh_from_db()
        if item.quantity > variant.stock:
            CartItem.objects.filter(pk=item.pk).delete()
            raise OutOfStockError("No hay existencias suficientes para esa cantidad.")
        return
    current = int(request.session.get(CART_KEY, {}).get(str(size_id), 0))
    if current + quantity > variant.stock: raise OutOfStockError("No hay existencias suficientes para esa cantidad.")
    cart = request.session.get(CART_KEY, {}); cart[str(size_id)] = current + quantity; request.session[CART_KEY] = cart; request.session.modified = True

def update_item(request, size_id, quantity):
    if not isinstance(quantity, int) or quantity < 1: raise InvalidQuantityError("La cantidad debe ser un entero mayor que cero.")
    variant = ProductSize.objects.get(pk=size_id, product__is_active=True)
    if quantity > variant.stock: raise OutOfStockError("No hay existencias suficientes para esa cantidad.")
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        CartItem.objects.update_or_create(cart=cart, variant=variant, defaults={"quantity": quantity})
        return
    cart = request.session.get(CART_KEY, {}); cart[str(size_id)] = quantity; request.session[CART_KEY] = cart; request.session.modified = True

def remove_item(request, size_id):
    if request.user.is_authenticated:
        CartItem.objects.filter(cart__user=request.user, variant_id=size_id).delete()
        return
    cart = request.session.get(CART_KEY, {}); cart.pop(str(size_id), None); request.session[CART_KEY] = cart; request.session.modified = True

def merge_session_cart(request, user):
    cart = request.session.get(CART_KEY, {})
    with transaction.atomic():
        user_cart, _ = Cart.objects.get_or_create(user=user)
        for size_key, quantity in cart.items():
            try:
                variant = ProductSize.objects.get(pk=int(size_key), product__is_active=True)
                if variant.stock < 1: continue
                current, created = CartItem.objects.get_or_create(cart=user_cart, variant=variant, defaults={"quantity": min(variant.stock, int(quantity))})
                if not created:
                    current.quantity = min(variant.stock, current.quantity + int(quantity)); current.save(update_fields=["quantity"])
            except (ValueError, TypeError, ProductSize.DoesNotExist): continue
    request.session.pop(CART_KEY, None)
