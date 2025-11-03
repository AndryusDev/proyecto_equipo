from django.urls import path
from .views import VistaLogin
from . import views


urlpatterns = [

    path('', views.lista_pedidos, name='lista_pedidos'),
]
