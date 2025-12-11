# Tienda Somai

Tienda Somai es una plataforma de comercio electrónico diseñada para la venta de moda online, ofreciendo las últimas tendencias en ropa y accesorios para hombre y mujer. Este proyecto está construido utilizando Django como framework backend.

## Características Principales

*   **Catálogo de Productos:** Exploración de prendas organizadas por categorías (Hombre, Mujer, etc.).
*   **Detalle de Producto:** Visualización detallada de cada prenda, incluyendo descripción, precio y selección de variantes.
*   **Carrito de Compras:** Funcionalidad completa para agregar productos, gestionar cantidades y visualizar el total.
*   **Gestión de Usuarios:** Sistema de registro e inicio de sesión personalizado para clientes.
*   **Procesamiento de Pagos:** Integración con **Stripe** para realizar pagos seguros.
*   **Gestión de Pedidos:** Seguimiento del estado de los pedidos (Carrito, Pendiente, Procesado, Enviado, Entregado).

## Tecnologías Utilizadas

*   **Backend:** Python, Django
*   **Base de Datos:** SQLite (por defecto)
*   **Frontend:** HTML5, CSS3 (Bootstrap), JavaScript
*   **Pagos:** Stripe API

## Estructura del Proyecto

El proyecto se encuentra bajo la carpeta `ProyectoTienda` y sigue la estructura estándar de Django:

*   `ProyectoTienda/`: Configuración principal del proyecto.
*   `tiendaApp/`: Aplicación principal que contiene la lógica de negocio.
    *   `models.py`: Definición de modelos (Cliente, Prenda, Pedido, etc.).
    *   `views.py`: Controladores de las vistas y lógica de la aplicación.
    *   `urls.py`: Definición de rutas.
    *   `templates/`: Plantillas HTML para las vistas.
    *   `static/`: Archivos estáticos (CSS, JS, imágenes).

## Manejo de Errores

El proyecto incluye plantillas personalizadas para los errores **404 (Página no encontrada)** y **500 (Error interno del servidor)**.

**Instrucciones para probar las páginas de error:**

1.  En el archivo `ProyectoTienda/settings.py`, cambiar la configuración a producción:
    ```python
    DEBUG = False
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
    ```
2.  Ejecutar el servidor en modo inseguro (para servir estáticos sin debug):
    ```bash
    python manage.py runserver --insecure
    ```
3.  **Probar Error 404:** Intentar acceder a una URL que no existe (ej: `http://127.0.0.1:8000/pagina-inexistente`).
4.  **Probar Error 500:** Acceder a la ruta de prueba habilitada: `http://127.0.0.1:8000/test-500/`.

## Instalación y Ejecución

Sigue estos pasos para ejecutar el proyecto localmente:

1.  **Navegar al directorio del proyecto:**
    ```bash
    cd ProyectoTienda
    ```

2.  **Crear un entorno virtual (opcional pero recomendado):**
    ```bash
    python -m venv venv
    # En Windows
    venv\Scripts\activate
    # En macOS/Linux
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    Asegúrate de tener instaladas las librerías necesarias.
    ```bash
    pip install django stripe
    ```

4.  **Configurar variables de entorno:**
    Asegúrate de configurar tus claves de API de Stripe en `settings.py`.

5.  **Aplicar migraciones:**
    ```bash
    python manage.py migrate
    ```

6.  **Ejecutar el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```

7.  **Acceder a la aplicación:**
    Abre tu navegador y visita `http://127.0.0.1:8000/`.

## Funcionalidades Implementadas (Entrega E4)

Este proyecto cumple con los siguientes objetivos y funcionalidades opcionales propuestas para la entrega:

### [E4a] Funcionalidades añadidas en Django

*   **Opción 1 (1,25 puntos): Interacción enriquecida en el cliente con JavaScript.**
    *   Se ha implementado lógica en JavaScript en la vista de detalles de producto (`detalles_prenda.html`) para gestionar dinámicamente el stock disponible según la variante seleccionada, deshabilitando el botón de compra si no hay existencias.
*   **Opción 2 (0,75 puntos): Uso de vistas basadas en clases.**
    *   Se utilizan `ListView` para el listado de prendas y `DetailView` para la ficha de producto en `tiendaApp/views.py`.
*   **Opción 3 (0,75 puntos): Uso de formularios en la aplicación pública.**
    *   Implementación de formularios para registro (`RegistroForm`), inicio de sesión (`LoginForm`) y añadir al carrito (`AddToCartForm`).
*   **Opción 4 (0,50 puntos): Personalizar la aplicación de administración.**
    *   Se ha personalizado el panel de administración (`admin.py`) para el modelo `Pedido`, incluyendo filtros, campos de solo lectura y la visualización de items de pedido en línea (`ItemPedidoInline`).

### [E4b] Desarrollo con Vue (Extra)

*   **Desarrollar la SPA con Vue (0,3 puntos):**
    *   Se incluye una aplicación independiente en la carpeta `agendaVue/` que implementa una agenda de contactos (SPA) con funcionalidades de listar, crear y borrar contactos.
*   **Incluir capacidades micro-semánticas (0,2 puntos):**
    *   La aplicación Vue incluye marcado de datos estructurados **JSON-LD** en su `index.html` para definir la aplicación como una `WebApplication`.

## Licencia

Este proyecto es de uso académico/privado.
