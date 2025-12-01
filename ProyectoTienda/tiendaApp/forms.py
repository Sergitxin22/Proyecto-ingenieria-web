from django import forms
from .models import VariantePrenda

class AddToCartForm(forms.Form):
    variante = forms.ModelChoiceField(
        queryset=VariantePrenda.objects.none(),
        label="Talla / Tipo"
    )
    cantidad = forms.IntegerField(
        min_value=1,
        label="Cantidad"
    )

    # Para pasar las variantes de la prenda
    def __init__(self, *args, **kwargs):
        prenda = kwargs.pop("prenda", None)
        super().__init__(*args, **kwargs)
        if prenda:
            self.fields["variante"].queryset = prenda.variantes.all()

class LoginForm(forms.Form):
    nombreUsuario = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )