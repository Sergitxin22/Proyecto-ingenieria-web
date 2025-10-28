from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse('primera vista')
# Create your views here.
