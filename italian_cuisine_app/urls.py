from django.urls import path
from .views import VistaLogin, VistaLogout, DashboardView, PanelPrincipalView, PlatosCategoriasView, AgregarCategoriaView, AgregarPlatoView, EliminarCategoriaView, EliminarPlatoView, PedidosView, MisPedidosView, CrearPedidoView
from .views import VistaLogin
from . import views


urlpatterns = [
    path('', views.lista_pedidos, name='lista_pedidos'),
    path('login/', VistaLogin.as_view(), name='login'),
    path('logout/', VistaLogout.as_view(), name='logout'),
    path('panel/', PanelPrincipalView.as_view(), name='panel_principal'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('empleados/', views.UserListView.as_view(), name='empleados'),
    path('empleados/nuevo/', views.EmpleadoCreateView.as_view(), name='empleado_create'),
    path('empleados/<int:pk>/', views.EmpleadoDetailView.as_view(), name='empleado_detail'),
    path('empleados/<int:pk>/edit/', views.EmpleadoUpdateView.as_view(), name='empleado_edit'),
    path('empleados/<int:pk>/delete/', views.EmpleadoDeleteView.as_view(), name='empleado_delete'),
    path('panel/platos/', PlatosCategoriasView.as_view(), name='platos_categorias'),
    path('panel/platos/agregar-categoria/', AgregarCategoriaView.as_view(), name='agregar_categoria'),
    path('panel/platos/agregar-plato/', AgregarPlatoView.as_view(), name='agregar_plato'),
    path('panel/platos/eliminar-categoria/<int:pk>/', EliminarCategoriaView.as_view(), name='eliminar_categoria'),
    path('panel/platos/eliminar-plato/<int:pk>/', EliminarPlatoView.as_view(), name='eliminar_plato'),
    #pedidos
    path('panel/pedidos/', PedidosView.as_view(), name='pedidos'),
    path('panel/pedidos/crear/', CrearPedidoView.as_view(), name='crear_pedido'),
    path('panel/mis-pedidos/', MisPedidosView.as_view(), name='mis_pedidos'),
]
