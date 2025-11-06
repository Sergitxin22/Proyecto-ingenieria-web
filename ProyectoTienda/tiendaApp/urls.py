from django.urls import path
from .import views

urlpatterns=[
    path('', views.index, name='listaTienda'),
    path('prendas/', views.lista_prendas, name='lista_prendas'),
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('prendas/<int:pk>/', views.detalle_prenda, name='detalle_prenda'),
    path('pedidos/<int:pk>/', views.detalle_pedido, name='detalle_pedido'),
    path('clientes/<int:pk>/', views.detalle_cliente, name='detalle_cliente'),
]