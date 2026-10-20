from django.db import models

class ContactMessage(models.Model):
    SUBJECTS = [("order", "Seguimiento de pedido"), ("return", "Devolución o cambio"), ("product", "Información de producto"), ("personalization", "Personalización"), ("other", "Otro")]
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=24, choices=SUBJECTS)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    class Meta: ordering = ("-created_at",)
    def __str__(self): return f"{self.name} · {self.get_subject_display()}"
