from django.urls import path
from .views import VistaLogin, VistaLogout, DashboardView, PanelPrincipalView

urlpatterns = [
    path('login/', VistaLogin.as_view(), name='login'),
    path('logout/', VistaLogout.as_view(), name='logout'),
    path('panel/', PanelPrincipalView.as_view(), name='panel_principal'),  # redirige al dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),         # muestra el dashboard
]
