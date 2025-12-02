from .models import Categoria, Cliente
from .carrito import Carrito


def categorias_processor(request):
    categorias = Categoria.objects.all()
    return {
        "categorias": categorias
    }

def carrito_processor(request):
    """Agrega información del carrito a todos los templates"""
    carrito = Carrito(request)
    return {
        'carrito_total_items': len(carrito),
        'carrito_precio_total': carrito.get_total_precio()
    }

def cliente_logueado(request):
    cliente = None
    cliente_id = request.session.get("cliente_id")

    if cliente_id:
        try:
            cliente = Cliente.objects.get(id=cliente_id)
        except Cliente.DoesNotExist:
            cliente = None

    return {"cliente": cliente}