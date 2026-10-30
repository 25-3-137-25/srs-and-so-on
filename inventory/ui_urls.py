from django.urls import path
from django.shortcuts import render


def inventory_page(request):
    return render(request, 'inventory/list.html')


urlpatterns = [
    path('', inventory_page, name='inventory-page'),
]