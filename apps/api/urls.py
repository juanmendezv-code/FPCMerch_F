from django.urls import path
from . import views

app_name = "api"
urlpatterns = [
    path("v1/categories/", views.categories_api, name="categories-v1"),
    path("v1/products/", views.products_api, name="products-v1"),
    path("v1/products/<slug:slug>/", views.product_detail_api, name="product-detail-v1"),
    path("productos/", views.products_api, name="products"),
    path("productos/<slug:slug>/", views.product_detail_api, name="product-detail"),
    path("buscar/", views.search_api, name="search"),
    path("categorias/", views.categories_api, name="categories"),
    path("carrito/", views.cart_api, name="cart"),
    path("carrito/agregar/", views.cart_add_api, name="cart-add"),
    path("carrito/actualizar/", views.cart_update_api, name="cart-update"),
    path("carrito/eliminar/", views.cart_remove_api, name="cart-remove"),
]
