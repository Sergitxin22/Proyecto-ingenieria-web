from django.contrib import admin
from .models import Cliente, Prenda, Pedido

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Prenda)
admin.site.register(Pedido)