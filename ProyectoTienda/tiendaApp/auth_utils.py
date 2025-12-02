import secrets
from .models import Sesion, Cliente

def generar_token():
    """Genera un token único y seguro de 64 caracteres hexadecimales"""
    return secrets.token_hex(32)

def crear_sesion_usuario(cliente):
    """Crea una nueva sesión con token para el cliente"""
    # Desactivar sesiones anteriores del cliente
    Sesion.objects.filter(cliente=cliente, activo=True).update(activo=False)
    
    # Crear nueva sesión
    token = generar_token()
    sesion = Sesion.objects.create(
        cliente=cliente,
        token=token,
        activo=True
    )
    return token

def validar_token(token):
    """
    Valida si un token es válido y está activo
    Retorna el cliente asociado si es válido, None en caso contrario
    """
    try:
        sesion = Sesion.objects.get(token=token, activo=True)
        return sesion.cliente
    except Sesion.DoesNotExist:
        return None

def obtener_cliente_por_token(request):
    """
    Obtiene el cliente autenticado a través del token en la sesión
    """
    token = request.session.get('auth_token')
    if token:
        return validar_token(token)
    return None

def cerrar_sesion(token):
    """Desactiva una sesión específica"""
    try:
        sesion = Sesion.objects.get(token=token, activo=True)
        sesion.activo = False
        sesion.save()
        return True
    except Sesion.DoesNotExist:
        return False
