from django import forms
from unfold.widgets import (
    UnfoldAdminSelectWidget,
    UnfoldAdminTextInputWidget
)

class ProductoSelectWidget(UnfoldAdminSelectWidget):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)

        # Verifica si `value` es una instancia de `ModelChoiceIteratorValue`
        if isinstance(value, forms.models.ModelChoiceIteratorValue):
            value = value.value  # Extrae el valor real (ID) del producto

        # Ahora, `value` debe ser el ID del producto
        if value:
            product = self.choices.queryset.get(pk=value)
            precio = product.precio  # Reemplaza `precio` con el nombre del campo correspondiente en tu modelo
            option['attrs']['data-precio'] = precio

        return option
    
    