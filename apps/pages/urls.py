from django.urls import path
from .views import home, info_page

app_name = "pages"
urlpatterns = [path("", home, name="home"), path("informacion/<slug:slug>/", info_page, name="info")]
