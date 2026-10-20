from django.urls import path
from . import views

app_name = "orders"
urlpatterns = [path("checkout/", views.checkout, name="checkout"), path("pedido/<str:number>/", views.order_detail, name="detail"), path("pedido/<str:number>/confirmacion/", views.confirmation, name="confirmation")]
