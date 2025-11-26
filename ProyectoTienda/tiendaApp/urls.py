from django.urls import path
from .import views

urlpatterns=[
    path('', views.base, name='home'),
    path('prendas/', views.PrendaListView.as_view(), name='lista_prendas'),
    path('pedidos/', views.PedidoListView.as_view(), name='lista_pedidos'),
    path('clientes/', views.ClienteListView.as_view(), name='lista_clientes'),
    path('categorias/', views.CategoriaListView.as_view(), name='lista_categorias'),
    path('prendas/<int:pk>/', views.PrendaDetailView.as_view(), name='detalles_prenda'),
    path('pedidos/<int:pk>/', views.PedidoDetailView.as_view(), name='detalles_pedido'),
    path('clientes/<int:pk>/', views.ClienteDetailView.as_view(), name='detalles_cliente'),
    path('categorias/<int:pk>/', views.CategoriaDetailView.as_view(), name='detalles_categoria'),
]