from django.urls import path
from .views import (
    VistaLogin, VistaLogout, DashboardView, PanelPrincipalView,
    PlatosCategoriasView, AgregarCategoriaView, AgregarPlatoView,
    EliminarCategoriaView, EliminarPlatoView,
    PedidosView, CrearPedidoView, MisPedidosView, CerrarPedidoView,
    PanelMesasView, cambiar_estado_mesa, InicioView
)
from django.shortcuts import redirect
from .models import Empleado
from . import views

def redireccion_inicio(request):
    """Redirige al dashboard o a mis_pedidos según el cargo."""
    if not request.user.is_authenticated:
        return redirect('login')

    empleado = Empleado.objects.filter(user=request.user).first()
    if empleado:
        if empleado.cargo == 'administrador':
            return redirect('dashboard')
        elif empleado.cargo == 'mesero':
            return redirect('mis_pedidos')

    # Por defecto
    return redirect('mis_pedidos')

urlpatterns = [
    # Página principal (lista de pedidos general)
    path('', redireccion_inicio, name='inicio'),  # 👈 Condicional aplicado aquí

    # Autenticación
    path('login/', VistaLogin.as_view(), name='login'),
    path('logout/', VistaLogout.as_view(), name='logout'),

    # Panel general
    path('panel/', PanelPrincipalView.as_view(), name='panel_principal'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Empleados
    path('empleados/', views.UserListView.as_view(), name='empleados'),
    path('empleados/nuevo/', views.EmpleadoCreateView.as_view(), name='empleado_create'),
    path('empleados/<int:pk>/', views.EmpleadoDetailView.as_view(), name='empleado_detail'),
    path('empleados/<int:pk>/edit/', views.EmpleadoUpdateView.as_view(), name='empleado_edit'),
    path('empleados/<int:pk>/delete/', views.EmpleadoDeleteView.as_view(), name='empleado_delete'),

    # Platos y Categorías
    path('panel/platos/', PlatosCategoriasView.as_view(), name='platos_categorias'),
    path('panel/platos/agregar-categoria/', AgregarCategoriaView.as_view(), name='agregar_categoria'),
    path('panel/platos/agregar-plato/', AgregarPlatoView.as_view(), name='agregar_plato'),
    path('panel/platos/eliminar-categoria/<int:pk>/', EliminarCategoriaView.as_view(), name='eliminar_categoria'),
    path('panel/platos/eliminar-plato/<int:pk>/', EliminarPlatoView.as_view(), name='eliminar_plato'),

    # 🧾 Pedidos
    path('panel/pedidos/', PedidosView.as_view(), name='pedidos'),
    path('panel/pedidos/crear/', CrearPedidoView.as_view(), name='crear_pedido'),
    path('panel/mis-pedidos/', MisPedidosView.as_view(), name='mis_pedidos'),
    path('panel/pedido/<int:pk>/cerrar/', CerrarPedidoView.as_view(), name='cerrar_pedido'),

    # 🍽️ Platos
    path('plato/<int:pk>/', views.obtener_plato, name='obtener_plato'),
    path('plato/editar/', views.EditarPlatoView.as_view(), name='editar_plato'),

    # 🪑 Mesas
    path("panel/mesas/", PanelMesasView.as_view(), name="panel_mesas"),
    path("mesa/<int:pk>/cambiar/", cambiar_estado_mesa, name="cambiar_estado_mesa"),

]
