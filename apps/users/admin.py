from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from .models import User

class EmailUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = EmailUserCreationForm
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "is_staff", "ciudad")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = ((None, {"fields": ("email", "password")}), ("Información personal", {"fields": ("first_name", "last_name", "telefono", "ciudad")}), ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}), ("Fechas", {"fields": ("last_login", "date_joined")}))
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "is_staff", "is_superuser")}),)
