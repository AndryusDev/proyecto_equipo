from django.urls import path
from .views import VistaLogin, VistaLogout, DashboardView, PanelPrincipalView, PlatosCategoriasView, AgregarCategoriaView, AgregarPlatoView, EliminarCategoriaView, EliminarPlatoView
from .views import VistaLogin
from . import views


urlpatterns = [

    path('', views.lista_pedidos, name='lista_pedidos'),
    path('login/', VistaLogin.as_view(), name='login'),
    path('logout/', VistaLogout.as_view(), name='logout'),
    path('panel/', PanelPrincipalView.as_view(), name='panel_principal'),  # redirige al dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),         # muestra el dashboard

    path('panel/platos/', PlatosCategoriasView.as_view(), name='platos_categorias'),
    path('panel/platos/agregar-categoria/', AgregarCategoriaView.as_view(), name='agregar_categoria'),
    path('panel/platos/agregar-plato/', AgregarPlatoView.as_view(), name='agregar_plato'),
    path('panel/platos/eliminar-categoria/<int:pk>/', EliminarCategoriaView.as_view(), name='eliminar_categoria'),
    path('panel/platos/eliminar-plato/<int:pk>/', EliminarPlatoView.as_view(), name='eliminar_plato'),


]
