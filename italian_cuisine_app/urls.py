from django.urls import path
from .views import VistaLogin, VistaLogout, DashboardView, PanelPrincipalView
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
]
