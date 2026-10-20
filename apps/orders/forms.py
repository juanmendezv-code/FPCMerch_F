from django import forms

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(label="Dirección de envío", max_length=240)
    city = forms.CharField(label="Ciudad", max_length=100)
    phone = forms.CharField(label="Teléfono", max_length=30)
    payment_method = forms.ChoiceField(label="Método de pago (simulación)", choices=(("demo_card", "Tarjeta de demostración"), ("cash_demo", "Pago contra entrega simulado")))
