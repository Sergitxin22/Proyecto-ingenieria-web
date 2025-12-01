from .models import Categoria
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