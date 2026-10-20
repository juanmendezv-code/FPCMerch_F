from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, render
from .forms import LoginForm, ProfileForm, RegistrationForm
from apps.cart.services import merge_session_cart
from apps.orders.models import Order

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(request, email=form.cleaned_data["email"], password=form.cleaned_data["password"])
        if user:
            login(request, user)
            if not form.cleaned_data["remember"]:
                request.session.set_expiry(0)
            merge_session_cart(request, user)
            return redirect(request.GET.get("next") or "pages:home")
        messages.error(request, "No pudimos iniciar sesión con esos datos.")
    return render(request, "users/login.html", {"form": form})

def register_view(request):
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="apps.users.backends.EmailBackend")
        merge_session_cart(request, user)
        messages.success(request, "Tu cuenta fue creada.")
        return redirect("pages:home")
    return render(request, "users/register.html", {"form": form})

@require_POST
def logout_view(request):
    logout(request)
    return redirect("pages:home")

@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Información actualizada.")
        return redirect("users:profile")
    return render(request, "users/profile.html", {"form": form, "orders": Order.objects.filter(user=request.user).order_by("-created_at")})
