from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Sum, ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from .forms import ProductForm, SizeFormSet
from .models import Category, Product
from .services import filtered_products
from apps.api.external import usd_estimate

def catalog(request):
    page = Paginator(filtered_products(request.GET), 12).get_page(request.GET.get("page"))
    return render(request, "products/catalog.html", {"page_obj": page, "products": page.object_list, "filters": request.GET})

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.prefetch_related("sizes"), slug=slug, is_active=True)
    return render(request, "products/detail.html", {"product": product, "usd_price": usd_estimate(product.price)})

class StaffMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self): return self.request.user.is_staff

class ProductManagementList(StaffMixin, ListView):
    model = Product
    template_name = "management/product_list.html"
    context_object_name = "products"
    paginate_by = 15
    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        qs = Product.objects.select_related("category").annotate(stock_sum=Sum("sizes__stock")).order_by("-created_at", "pk")
        return qs.filter(name__icontains=query) if query else qs

class ProductCreate(StaffMixin, CreateView):
    model = Product; form_class = ProductForm; template_name = "management/product_form.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs); ctx["size_formset"] = kwargs.get("size_formset") or SizeFormSet(self.request.POST or None, self.request.FILES or None); return ctx
    def form_valid(self, form):
        ctx = self.get_context_data(); formset = ctx["size_formset"]
        if not formset.is_valid(): return self.form_invalid(form)
        self.object = form.save(); formset.instance = self.object; formset.save(); messages.success(self.request, "Producto creado."); return redirect("products:manage")

class ProductUpdate(StaffMixin, UpdateView):
    model = Product; form_class = ProductForm; template_name = "management/product_form.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs); ctx["size_formset"] = kwargs.get("size_formset") or SizeFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object); return ctx
    def form_valid(self, form):
        ctx = self.get_context_data(); formset = ctx["size_formset"]
        if not formset.is_valid(): return self.form_invalid(form)
        self.object = form.save(); formset.instance = self.object; formset.save(); messages.success(self.request, "Producto actualizado."); return redirect("products:manage")

class ProductDelete(StaffMixin, DeleteView):
    model = Product; template_name = "management/product_confirm_delete.html"; success_url = reverse_lazy("products:manage")
    def form_valid(self, form):
        try:
            self.object.delete()
            messages.success(self.request, "Producto eliminado.")
        except ProtectedError:
            self.object.is_active = False; self.object.save(update_fields=["is_active"])
            messages.warning(self.request, "El producto tiene pedidos y se desactivó en lugar de eliminarse.")
        return redirect(self.success_url)
