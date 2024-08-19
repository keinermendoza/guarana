from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from unfold.widgets import UnfoldAdminSelectWidget
from .models import (
    Ralada,
    VentaItem,
    Producto,
    UsoMetodoPago,
    Produccion,
    CompraVidros,
    ProduccionDetalle
)
from .widgets import ProductoSelectWidget


from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

class ProduccionDetalleFormset(BaseInlineFormSet):
    """
    Validation through two inlines
    """
    def clean(self):
        super(ProduccionDetalleFormset, self).clean()
        peso_total = 0
        print(self.instance.tipo_guarana)
        for form in self.forms:
            if not form.is_valid():
                return # other errors exist, so don't bother
            
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                producto = form.cleaned_data.get('producto')
                cantidad = form.cleaned_data.get('cantidad')

                if producto:
                    if cantidad:
                        peso = producto.peso * cantidad
                        peso_total += peso

                    if not self.instance.peso_maximo:
                        form.add_error('producto', forms.ValidationError(
                            "Não pode registrar produtos até registrar o peso final da ralada"
                        ))
                
                    if self.instance.tipo_guarana and producto.tipo_guarana != self.instance.tipo_guarana:
                        form.add_error('producto', forms.ValidationError(
                            f"Produto pertence a um tipo de guarana ({producto.tipo_guarana}) que não corresponde com o tipo de guarana da ralada ({self.instance.tipo_guarana})"
                        ))
  
        if self.instance.peso_maximo and self.instance.peso_maximo < peso_total:
            raise ValidationError(
                f"A soma do peso dos produtos ({peso_total}g) Não pode superar o peso final da Ralada ({self.instance.peso_maximo}g)"
            )
    
class InlineProduccionDetalleForm(forms.ModelForm):
    class Meta:
        model = ProduccionDetalle
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Prepopulates the product options using the related tipo_guarana if the instance already exists. 
        """
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if instance and instance.produccion.ralada.saco.tipo_guarana:
            self.fields['producto'].queryset = Producto.objects.filter(tipo_guarana=instance.produccion.ralada.saco.tipo_guarana)
        else:
            self.fields['producto'].queryset = Producto.objects.none()
            
        
class ProduccionForm(forms.ModelForm):
    class Meta:
        model = Produccion
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
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

class RaladaInlineFormset(BaseInlineFormSet):
    def clean(self):
        super(RaladaInlineFormset, self).clean()
        peso_maximo = 0
        saco = ''
        for form in self.forms:
            if not form.is_valid():
                return # other errors exist, so don't bother
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                peso_maximo = form.cleaned_data.get('peso_final')
                saco = form.cleaned_data.get('saco')

        self.instance.peso_maximo = peso_maximo
        self.instance.tipo_guarana = saco.tipo_guarana
            
class InlineVentaItemAddForm(forms.ModelForm):
    class Meta:
        model = VentaItem
        fields = "__all__"
        widgets = {
            'producto':ProductoSelectWidget(attrs={'data-producto':'update-price'}),
            'precio': forms.TextInput(attrs={
                'class': 'pointer-events-none bg-gray-600	border bg-white font-medium min-w-20 rounded-md shadow-sm text-gray-500 text-sm dark:bg-gray-900 dark:border-gray-700 dark:text-gray-300  dark:group-[.errors]:border-red-500  px-3 py-2 w-full max-w-2xl'
                ,"tabindex":"-1"
                , "style":"background-color:#eee"
            }),  
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

class InlineCompraVidrosForm(forms.ModelForm):
    class Meta:
        fields = ["precio", "cantidad"]
        model = CompraVidros
        widgets = {
            'precio': forms.TextInput(attrs={
                'class': 'pointer-events-none bg-gray-600	border bg-white font-medium min-w-20 rounded-md shadow-sm text-gray-500 text-sm dark:bg-gray-900 dark:border-gray-700 dark:text-gray-300  dark:group-[.errors]:border-red-500  px-3 py-2 w-full max-w-2xl'
                ,"tabindex":"-1"
                , "style":"background-color:#eee"
            }),  
        }