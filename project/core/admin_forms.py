from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from unfold.widgets import UnfoldAdminSelectWidget
from .models import Ralada, VentaItem, Producto, UsoMetodoPago, Produccion
from .widgets import ProductoSelectWidget


from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet


class ProduccionDetalleFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()

  
        
class ProduccionForm(forms.ModelForm):
    class Meta:
        model = Produccion
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        # Obtén los formsets relacionados
        # proceso_formset = self.formsets.get('proceso_formset')
        # producto_formset = self.formsets.get('producto_formset')
        proceso_formset = None
        producto_formset = None

        print(self.formsets)
        # if not proceso_formset or not producto_formset:
        #     return cleaned_data

        # # Obtén el tipo de café que se está procesando
        # tipo_cafe_procesado = self.cleaned_data.get('tipo_cafe')

        # # Itera sobre los productos producidos y verifica que correspondan con el tipo de café procesado
        # for producto_form in producto_formset.forms:
        #     if producto_form.cleaned_data and not producto_form.cleaned_data.get('DELETE'):
        #         tipo_cafe_producto = producto_form.cleaned_data.get('tipo_cafe')

        #         if tipo_cafe_producto != tipo_cafe_procesado:
        #             raise ValidationError(
        #                 f"El producto '{producto_form.cleaned_data.get('nombre_producto')}' no corresponde al tipo de café procesado ({tipo_cafe_procesado.nombre})."
        #             )

        return cleaned_data
class InlineRaladaForm(forms.ModelForm):
    input1 = forms.IntegerField(label='Vasilha inicial 1', required=False)
    input2 = forms.IntegerField(label='Vasilha inicial 2', required=False)

    class Meta:
        model = Ralada
        fields = ['cantidad_bastones' , 'input1', 'input2', 'peso_inicial', 'sobra_inicial', 'sobra_final', 'peso_final', 'saco', 'numero' ,'fecha_ralada']  # Añade el campo total_field
        widgets = {
            'saco':UnfoldAdminSelectWidget(attrs={
                'data-trigger':'handle_update_product_options',
                'x-on:change':'$dispatch("update_product_inline_options")'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['input1'].widget.attrs.update({'class': 'input1 border bg-white font-medium min-w-20 rounded-md shadow-sm text-gray-500 text-sm focus:ring focus:ring-primary-300 focus:border-primary-600 focus:outline-none group-[.errors]:border-red-600 group-[.errors]:focus:ring-red-200 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-300 dark:focus:border-primary-600 dark:focus:ring-primary-700 dark:focus:ring-opacity-50 dark:group-[.errors]:border-red-500 dark:group-[.errors]:focus:ring-red-600/40 px-3 py-2 w-full max-w-2xl', 'oninput': 'updateTotal(this)'})
        self.fields['input2'].widget.attrs.update({'class': 'input2 border bg-white font-medium min-w-20 rounded-md shadow-sm text-gray-500 text-sm focus:ring focus:ring-primary-300 focus:border-primary-600 focus:outline-none group-[.errors]:border-red-600 group-[.errors]:focus:ring-red-200 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-300 dark:focus:border-primary-600 dark:focus:ring-primary-700 dark:focus:ring-opacity-50 dark:group-[.errors]:border-red-500 dark:group-[.errors]:focus:ring-red-600/40 px-3 py-2 w-full max-w-2xl', 'oninput': 'updateTotal(this)'})
        self.fields['peso_inicial'].widget.attrs.update({'data-peso':'peso_inicial'})

    class Media:
        js = [
            'admin/js/plus_two_inputs.js',
            'admin/js/handle_update_product_options.js'
        ]

           
class InlineVentaItemAddForm(forms.ModelForm):
    class Meta:
        model = VentaItem
        fields = "__all__"
        widgets = {
            'producto':ProductoSelectWidget(attrs={'data-producto':'update-price'}),
        }
        
    class Media:
        js = ["admin/js/update_price.js"]
    
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')  # Obtiene el producto
        precio = cleaned_data.get('precio')

        # Verifica si no hay precio y hay un producto seleccionado
        if not precio and producto:
            try:
                cleaned_data['precio'] = producto.precio
            except Producto.DoesNotExist:
                raise forms.ValidationError("El producto seleccionado no existe.")

        return cleaned_data
    
    
    
class InlineUsoMetodoPagoForm(forms.ModelForm):
    class Meta:
        model = UsoMetodoPago
        fields = "__all__"

    class Media:
        js = ['admin/js/vendas_formset.js']
