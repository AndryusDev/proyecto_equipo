from django.urls import path
from .views import VistaLogin, VistaLogout, DashboardView, PanelPrincipalView, PlatosCategoriasView, AgregarCategoriaView, AgregarPlatoView
from .views import VistaLogin
from . import views


urlpatterns = [

    path('', views.lista_pedidos, name='lista_pedidos'),
    path('login/', VistaLogin.as_view(), name='login'),
    path('logout/', VistaLogout.as_view(), name='logout'),
    path('panel/', PanelPrincipalView.as_view(), name='panel_principal'),  # redirige al dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),         # muestra el dashboard

    path('panel/platos/', PlatosCategoriasView.as_view(), name='platos_categorias'),

]
