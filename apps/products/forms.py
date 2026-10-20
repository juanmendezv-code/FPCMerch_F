from django import forms
from django.forms import inlineformset_factory
from PIL import Image, UnidentifiedImageError
from .models import Product, ProductSize

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "sku", "description", "price", "category", "image", "is_active", "is_featured")
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "size"):
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("La imagen no puede superar 5 MB.")
            try:
                image.seek(0); Image.open(image).verify(); image.seek(0)
            except (UnidentifiedImageError, OSError, ValueError):
                raise forms.ValidationError("Sube una imagen válida.")
        return image

class SizeForm(forms.ModelForm):
    size = forms.CharField(label="Talla", max_length=12, required=False)
    stock = forms.IntegerField(label="Existencias", min_value=0, required=False)

    class Meta:
        model = ProductSize
        fields = ("size", "stock")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        size = cleaned.get("size")
        stock = cleaned.get("stock")
        if size and stock is None:
            self.add_error("stock", "Indica el stock para esta talla.")
        elif stock is not None and not size:
            self.add_error("size", "Indica una talla o usa ÚNICA para variantes sin talla.")
        return cleaned

SizeFormSet = inlineformset_factory(Product, ProductSize, form=SizeForm, extra=1, min_num=1, validate_min=True, can_delete=True)
