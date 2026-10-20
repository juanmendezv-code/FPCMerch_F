from django.contrib import messages
from django.shortcuts import redirect, render
from .services import cart_data

def cart_page(request): return render(request, "cart/cart.html", cart_data(request))
