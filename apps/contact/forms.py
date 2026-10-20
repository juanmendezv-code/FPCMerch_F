from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "message")
        labels = {"name": "Nombre", "email": "Correo", "subject": "Asunto", "message": "Mensaje"}
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}
