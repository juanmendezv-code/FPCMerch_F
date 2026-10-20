from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from decimal import Decimal
from apps.cart.services import EmptyCartError, OutOfStockError, cart_data
from .forms import CheckoutForm
from .models import Order
from .services import create_order

@login_required
def checkout(request):
    summary = cart_data(request)
    if not summary["lines"]:
        messages.warning(request, "Agrega productos antes de continuar con la compra.")
        return redirect("cart:view")
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            order = create_order(request, form.cleaned_data)
            return redirect("orders:confirmation", number=order.number)
        except OutOfStockError as exc:
            messages.error(request, str(exc))
        except EmptyCartError as exc:
            messages.error(request, str(exc))
            return redirect("cart:view")
    shipping = Decimal("0") if summary["total"] >= Decimal(str(settings.FREE_SHIPPING_THRESHOLD)) else Decimal(str(settings.SHIPPING_FLAT_RATE))
    return render(request, "orders/checkout.html", {"form": form, "shipping": shipping, "grand_total": summary["total"] + shipping, **summary})

@login_required
def order_detail(request, number):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), number=number, user=request.user)
    return render(request, "orders/detail.html", {"order": order})

@login_required
def confirmation(request, number):
    return order_detail(request, number)
