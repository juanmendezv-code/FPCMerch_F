from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from .models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Correo")
    first_name = forms.CharField(label="Nombre")
    last_name = forms.CharField(label="Apellido")
    accept_terms = forms.BooleanField(label="Acepto los términos y condiciones")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        validate_password(password, self.instance)
        return password

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "telefono", "ciudad")
        labels = {"first_name": "Nombre", "last_name": "Apellido", "email": "Correo", "telefono": "Teléfono", "ciudad": "Ciudad"}

class LoginForm(forms.Form):
    email = forms.EmailField(label="Correo")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    remember = forms.BooleanField(label="Recordarme", required=False)
