from django import forms
from .models import Empleado


class EmpleadoModelForm(forms.ModelForm):
    class Meta:
        model = Empleado
        # Incluimos ahora también los datos personales opcionales
        fields = ['first_name', 'last_name', 'email', 'cargo', 'telefono']

    def save(self, commit=True):
        # Usamos el comportamiento por defecto de ModelForm
        empleado = super().save(commit=commit)
        return empleado
