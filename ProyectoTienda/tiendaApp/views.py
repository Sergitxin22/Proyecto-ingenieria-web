from django.shortcuts import render
from django.http import HttpResponse
from .models import Cliente, Prenda, Pedido

def index(request):
    return HttpResponse('primera vista')
# Create your views here.

def lista_prendas(request):
    prendas = Prenda.objects.all()
    context = {'prendas': prendas}
    return render(request, 'prendas/lista_prendas.html', context)
