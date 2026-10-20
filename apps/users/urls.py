from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path("cuenta/entrar/", views.login_view, name="login"),
    path("cuenta/registro/", views.register_view, name="register"),
    path("cuenta/salir/", views.logout_view, name="logout"),
    path("mi-cuenta/", views.profile_view, name="profile"),
]
