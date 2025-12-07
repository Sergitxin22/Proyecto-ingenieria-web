from django import forms
from .models import VariantePrenda

class AddToCartForm(forms.Form):
    variante = forms.ModelChoiceField(
        queryset=VariantePrenda.objects.none(),
        label="Talla / Tipo"
    )
    cantidad = forms.IntegerField(
        min_value=1,
        label="Cantidad",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )

    # Para pasar las variantes de la prenda
    def __init__(self, *args, **kwargs):
        prenda = kwargs.pop("prenda", None)
        super().__init__(*args, **kwargs)
        if prenda:
            self.fields["variante"].queryset = prenda.variantes.all()
            # Mostrar solo la descripción de la variante en el formulario
            self.fields["variante"].label_from_instance = lambda obj: obj.descripcion
    
    def clean(self):
        cleaned_data = super().clean()
        variante = cleaned_data.get("variante")
        cantidad = cleaned_data.get("cantidad")
        
        if variante and cantidad:
            if variante.stock == 0:
                raise forms.ValidationError(
                    f'No hay stock disponible de {variante}.'
                )
            if cantidad > variante.stock:
                raise forms.ValidationError(
                    f'Stock insuficiente. Solo hay {variante.stock} unidades disponibles de {variante}.'
                )
        
        return cleaned_data

class LoginForm(forms.Form):
    nombreUsuario = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

class RegistroForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    apellido = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(min_length=8, widget=forms.PasswordInput)