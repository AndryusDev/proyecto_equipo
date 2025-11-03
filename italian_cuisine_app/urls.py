from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('panel/', views.panel_principal, name='panel_principal'),
    path('empleados/', views.UserListView.as_view(), name='empleados'),
    path('empleados/nuevo/', views.EmpleadoCreateView.as_view(), name='empleado_create'),
    path('empleados/<int:pk>/', views.EmpleadoDetailView.as_view(), name='empleado_detail'),
    path('empleados/<int:pk>/edit/', views.EmpleadoUpdateView.as_view(), name='empleado_edit'),
    path('empleados/<int:pk>/delete/', views.EmpleadoDeleteView.as_view(), name='empleado_delete'),
]
