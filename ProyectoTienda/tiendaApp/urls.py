from django.urls import path
from .import views

urlpatterns=[
    path('', views.index, name='listaTienda'),
    path('prendas/', views.lista_prendas, name='lista_prendas'),
]