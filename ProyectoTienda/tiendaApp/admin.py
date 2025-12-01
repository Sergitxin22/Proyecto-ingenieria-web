from django.contrib import admin
from .models import Cliente, Prenda, Pedido, Categoria, FotoPrenda, VariantePrenda, ItemPedido

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Prenda)

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('subtotal',)
    
    def subtotal(self, obj):
        if obj.id:
            return f"${obj.subtotal()}"
        return "-"
    subtotal.short_description = 'Subtotal'

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'estado', 'precio_total', 'fecha')
    list_filter = ('estado', 'fecha')
    inlines = [ItemPedidoInline]
    readonly_fields = ('precio_total', 'fecha')

admin.site.register(Categoria)
admin.site.register(FotoPrenda)
admin.site.register(VariantePrenda)
admin.site.register(ItemPedido)