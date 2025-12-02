from .models import Categoria, Cliente
from .carrito import Carrito
from .auth_utils import obtener_cliente_por_token


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
    """Obtiene el cliente logueado validando su token"""
    cliente = obtener_cliente_por_token(request)
    
    # Si no hay token válido, limpiar la sesión
    if not cliente:
        request.session.pop('auth_token', None)
        request.session.pop('cliente_id', None)
    
    return {"cliente": cliente}