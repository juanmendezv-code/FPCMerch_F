import uuid
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.db.models import F
from apps.cart.services import CART_KEY, EmptyCartError, OutOfStockError, cart_data
from apps.cart.models import CartItem
from apps.products.models import ProductSize
from .models import Order, OrderItem

@transaction.atomic
def create_order(request, cleaned_data):
    summary = cart_data(request)
    if not summary["lines"]: raise EmptyCartError("El carrito está vacío.")
    subtotal = sum((line["subtotal"] for line in summary["lines"]), Decimal("0"))
    shipping = Decimal("0") if subtotal >= Decimal(str(settings.FREE_SHIPPING_THRESHOLD)) else Decimal(str(settings.SHIPPING_FLAT_RATE))
    order = Order.objects.create(user=request.user, number=f"FPC-{uuid.uuid4().hex[:10].upper()}", status=Order.Status.PAID,
        shipping_address=cleaned_data["shipping_address"], city=cleaned_data["city"], phone=cleaned_data["phone"],
        payment_method=cleaned_data["payment_method"], subtotal=subtotal, shipping_cost=shipping, total=subtotal + shipping)
    for line in summary["lines"]:
        variant = line["variant"]
        changed = ProductSize.objects.filter(pk=variant.pk, stock__gte=line["quantity"]).update(stock=F("stock") - line["quantity"])
        if not changed: raise OutOfStockError(f"Existencias insuficientes para {line['product'].name} ({line['size']}).")
        OrderItem.objects.create(order=order, product=line["product"], size=line["size"], quantity=line["quantity"], unit_price=line["product"].price)
    request.session[CART_KEY] = {}
    request.session.modified = True
    if request.user.is_authenticated:
        CartItem.objects.filter(cart__user=request.user).delete()
    return order
