# Explicación del Sistema de Tokens y Autenticación

Este documento detalla cómo se ha implementado el sistema de autenticación basado en tokens personalizados en el proyecto `ProyectoTienda`.

## 1. Objetivo
El objetivo principal es manejar la autenticación de usuarios (`Clientes`) sin depender del modelo de usuario por defecto de Django (`User`), permitiendo un control más flexible y personalizado sobre las sesiones y los datos del cliente.

## 2. Componentes Principales

### 2.1. Modelo `Sesion` (`models.py`)
Se ha creado un modelo específico para almacenar la información de la sesión activa de cada usuario.

```python
class Sesion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="sesion")
    token = models.CharField(max_length=256)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Token {self.token} de {self.cliente.nombre}"
```
- **cliente**: Relación con el modelo `Cliente`.
- **token**: Cadena única que identifica la sesión.
- **activo**: Booleano para invalidar sesiones sin borrarlas (útil para historial o "cerrar sesión en otros dispositivos").

### 2.2. Utilidades de Autenticación (`auth_utils.py`)
Este archivo encapsula toda la lógica de negocio relacionada con los tokens.

- **`generar_token()`**: Utiliza `secrets.token_hex(32)` para crear un string aleatorio y seguro de 64 caracteres.
- **`crear_sesion_usuario(cliente)`**:
    1. Invalida cualquier sesión activa previa del cliente (`activo=False`).
    2. Genera un nuevo token.
    3. Crea y guarda un nuevo registro en el modelo `Sesion`.
    4. Retorna el token generado.
- **`validar_token(token)`**: Busca una sesión activa con ese token. Si existe, retorna el objeto `Cliente` asociado; si no, retorna `None`.
- **`obtener_cliente_por_token(request)`**: Helper que extrae el token de `request.session['auth_token']` y llama a `validar_token`.
- **`cerrar_sesion(token)`**: Busca la sesión activa por token y la marca como inactiva (`activo=False`).

### 2.3. Integración en Vistas (`views.py`)

#### Login (`login_view`)
Cuando un usuario se loguea correctamente:
1. Se verifica email y contraseña contra el modelo `Cliente`.
2. Se llama a `crear_sesion_usuario(cliente)` para obtener un nuevo token.
3. Se guarda este token en la sesión de Django: `request.session["auth_token"] = token`.
4. Se guarda también el ID del cliente por conveniencia: `request.session["cliente_id"] = cliente.id`.

#### Logout (`logout_view`)
1. Se obtiene el token de la sesión.
2. Se llama a `cerrar_sesion(token)` para invalidarlo en la base de datos.
3. Se limpia la sesión de Django con `request.session.flush()`.

#### Protección de Rutas (`CheckoutView`)
En vistas sensibles como el checkout, se verifica la autenticación manualmente:
```python
cliente = obtener_cliente_por_token(request)
if not cliente:
    # Redirigir a login o mostrar error
```

### 2.4. Context Processor (`context_processor.py`)
Para que el usuario esté disponible en todas las plantillas (por ejemplo, para mostrar "Hola, Sergio" en el header), se usa un context processor:

- **`cliente_logueado(request)`**:
    1. Intenta obtener el cliente usando `obtener_cliente_por_token(request)`.
    2. Si el token no es válido o no existe, limpia las variables de sesión.
    3. Retorna `{'cliente': cliente}` para que esté disponible en los templates.

## 3. Flujo Completo
1. **Usuario ingresa credenciales**.
2. **Servidor valida** y genera un token único (ej: `a1b2...`).
3. **Servidor guarda** el token en la BD (`Sesion`) y en la cookie de sesión del navegador (`request.session`).
4. **En cada petición subsiguiente**, el `context_processor` lee el token de la sesión, consulta la BD para ver si es válido y recupera al `Cliente`.
5. **Al cerrar sesión**, el token se marca como inactivo en la BD y se borra del navegador.
