from django.urls import path
from .import views

urlpatterns=[
    path('', views.index, name='listaTienda'),
    path('prendas/', views.lista_prendas, name='lista_prendas'),
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('prendas/<int:pk>/', views.detalles_prenda, name='detalles_prenda'),
    path('pedidos/<int:pk>/', views.detalles_pedido, name='detalles_pedido'),
    path('clientes/<int:pk>/', views.detalles_cliente, name='detalles_cliente'),
    path('categorias/<int:pk>/', views.detalles_categoria, name='detalles_categoria'),
]