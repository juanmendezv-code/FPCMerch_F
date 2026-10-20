from django.urls import path
from . import views

app_name = "products"
urlpatterns = [
    path("catalogo/", views.catalog, name="catalog"),
    path("producto/<slug:slug>/", views.product_detail, name="detail"),
    path("gestion/productos/", views.ProductManagementList.as_view(), name="manage"),
    path("gestion/productos/nuevo/", views.ProductCreate.as_view(), name="create"),
    path("gestion/productos/<int:pk>/editar/", views.ProductUpdate.as_view(), name="update"),
    path("gestion/productos/<int:pk>/eliminar/", views.ProductDelete.as_view(), name="delete"),
]
