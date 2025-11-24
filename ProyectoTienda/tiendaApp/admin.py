from django.contrib import admin
from .models import Cliente, Prenda, Pedido,Categoria

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Prenda)
admin.site.register(Pedido)
admin.site.register(Categoria)