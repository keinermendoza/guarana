from typing import Any
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from unfold.widgets import (
    UnfoldAdminSelectWidget,
    UnfoldAdminTextInputWidget,
    UnfoldAdminIntegerRangeWidget,
    UnfoldAdminIntegerFieldWidget
)
from core.models import (
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

# TODO: update like VentaForm
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
                return 
            
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
        widgets = {
            'producto':UnfoldAdminSelectWidget(attrs={
                'data-target':'recive_update_product_options'
            })
        }

    def __init__(self, *args, **kwargs):
        """
        Prepopulates the product options using the related tipo_guarana if the instance already exists. 
        """
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if instance and instance.produccion.ralada.saco.tipo_guarana:
            self.fields['producto'].queryset = Producto.objects.filter(tipo_guarana=instance.produccion.ralada.saco.tipo_guarana)
        else:
            self.fields['producto'].queryset = Producto.objects.all()
            
        
class ProduccionForm(forms.ModelForm):
    class Meta:
        model = Produccion
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
  
class InlineRaladaForm(forms.ModelForm):
    # input1 = forms.IntegerField(label='Vasilha inicial 1', required=False)
    # input2 = forms.IntegerField(label='Vasilha inicial 2', required=False)

    class Meta:
        model = Ralada
        fields = ['cantidad_bastones' , 'peso_inicial', 'sobra_inicial', 'sobra_final', 'peso_final', 'saco', 'numero' ,'fecha_ralada']  # Añade el campo total_field
        widgets = {
            'saco':UnfoldAdminSelectWidget(attrs={
                'data-trigger':'handle_update_product_options',
                'x-on:change':'$dispatch("update_product_inline_options")'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['input1'].widget.attrs.update({'class': 'input1 border bg-white font-medium min-w-20 rounded-md shadow-sm text-gray-500 text-sm focus:ring focus:ring-primary-300 focus:border-primary-600 focus:outline-none group-[.errors]:border-red-600 group-[.errors]:focus:ring-red-200 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-300 dark:focus:border-primary-600 dark:focus:ring-primary-700 dark:focus:ring-opacity-50 dark:group-[.errors]:border-red-500 dark:group-[.errors]:focus:ring-red-600/40 px-3 py-2 w-full max-w-2xl', 'oninput': 'updateTotal(this)'})
        # self.fields['input2'].widget.attrs.update({'class': 'input2 border bg-white font-medium min-w-20 rounded-md shadow-sm text-gray-500 text-sm focus:ring focus:ring-primary-300 focus:border-primary-600 focus:outline-none group-[.errors]:border-red-600 group-[.errors]:focus:ring-red-200 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-300 dark:focus:border-primary-600 dark:focus:ring-primary-700 dark:focus:ring-opacity-50 dark:group-[.errors]:border-red-500 dark:group-[.errors]:focus:ring-red-600/40 px-3 py-2 w-full max-w-2xl', 'oninput': 'updateTotal(this)'})
        self.fields['peso_inicial'].widget.attrs.update({'data-peso':'peso_inicial'})

    class Media:
        js = [
            'admin/js/plus_two_inputs.js',
            'admin/js/handle_update_product_options.js'
        ]

# TODO: update like VentaForm
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

class VentaForm(forms.ModelForm):
    """
    Validates the main form using the asociated inlines
    Uses get_form in admin for insert formset as kwargs
    """
    class Meta:
        fields = "__all__"
        widgets = {
            'total': forms.TextInput(attrs={
                'class': 'pointer-events-none bg-gray-600	border bg-white font-medium min-w-20 rounded-md shadow-sm text-gray-500 text-sm dark:bg-gray-900 dark:border-gray-700 dark:text-gray-300  dark:group-[.errors]:border-red-500  px-3 py-2 w-full max-w-2xl'
                ,"tabindex":"-1"
                , "style":"background-color:#eee"
                , "autofocus":False
            })
         }

    def clean(self) -> dict[str, Any]:
        """
        first checks main form and asociated inlines are valid
        the checks the sells and posible discount match with main field 'total'
        """
        main_cleaned_data = super().clean()
        if not "total" in main_cleaned_data or not all([formset.is_valid() for formset in self.formsets]):
            return
        
        total_venta = main_cleaned_data["total"]
        total_monto_items = 0
        total_monto_compra_vidrios = 0

        for formset in self.formsets:
            for inline_form in formset:
                if inline_form.is_valid():
                    if cleaned_data := inline_form.clean():
                        if isinstance(inline_form, InlineVentaItemAddForm):
                            total_item = cleaned_data.get("cantidad") * cleaned_data.get("precio") 
                            total_monto_items += total_item

                        elif isinstance(inline_form, InlineCompraVidrosForm):
                            total_compra = cleaned_data.get("cantidad") * cleaned_data.get("precio") 
                            total_monto_compra_vidrios += total_compra
                        

        if total_venta != total_monto_items - total_monto_compra_vidrios:
            raise ValidationError("O total da venda não corresponde com os valores dos items e a compra de vidros")

    def __init__(self, *args, **kwargs):
        """
        extract the kwargs inserted in admin get_form method 
        """
        self.request = kwargs.pop('request')
        self.formsets = kwargs.pop('formsets')

        super().__init__(*args, **kwargs)

class InlineVentaItemFormset(BaseInlineFormSet):
    def clean(self) -> None:
        """
        checks that 'Venta' has almost one valid 'VentaItem' on it 
        """
        super(InlineVentaItemFormset, self).clean()
        valid_forms  = []
        for form in self.forms:
            if form.is_valid():
                valid_forms.append(form.clean())
            
        if not any(valid_forms):
            raise ValidationError("A venda debe ter pelo menos um produto registrado")

class InlineVentaItemAddForm(forms.ModelForm):
    """
    adds Custom widget for update price when change product select 
    adds script and custom data atribute for use as selector
    """
    
    def clean(self):
        """
        if there is price inserted dinamically by Javascript uses the product price
        NOTE: price is supose to be an 'soft-not-editable' field
        """
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')  # Obtiene el producto
        precio = cleaned_data.get('precio')

        if not precio and producto:
            try:
                cleaned_data['precio'] = producto.precio
            except Producto.DoesNotExist:
                raise forms.ValidationError("El producto seleccionado no existe.")
        return cleaned_data
    
    class Meta:
        model = VentaItem
        fields = "__all__"
        widgets = {
            'producto':ProductoSelectWidget(attrs={
                "style":"background-color:#f5d0fe",
                'x-on:change':'$dispatch("update-price")'
            }),
            'precio': forms.TextInput(attrs={
                'class': 'pointer-events-none bg-gray-600	border bg-white font-medium min-w-20 rounded-md shadow-sm text-gray-500 text-sm dark:bg-gray-900 dark:border-gray-700 dark:text-gray-300  dark:group-[.errors]:border-red-500  px-3 py-2 w-full max-w-2xl'
                ,"tabindex":"-1"
                , "style":"background-color:#eee"
                , "data-target":"item_precio_calculate_total"
            }),
            'cantidad': UnfoldAdminIntegerFieldWidget(attrs={
                'data-target':'item_cantidad_calculate_total',
                'x-on:input':'$dispatch("calculate")'
            })  
        }
    class Media:
        js = ["admin/js/update_price.js"]


class InlineUsoMetodoPagoFormset(BaseInlineFormSet):
    def clean(self):
        """
        checks that 'Venta' has almost one valid 'UsoMetodoPago' on it 
        """
        super(InlineUsoMetodoPagoFormset, self).clean() 
        valid_forms  = []
        total_pago = 0
        
        for form in self.forms:
            if form.is_valid():
                cleaned_data = form.clean()
                if "monto" in cleaned_data:
                    total_pago += cleaned_data["monto"]        
                valid_forms.append(cleaned_data)
        
        if not any(valid_forms):
            raise ValidationError("A venta requer pelo menos um metodo de pago")
    
        if total_pago != self.instance.total:
            raise ValidationError(f"o total pagado ({total_pago}) não corresponde com o total da venda ({self.instance.total})")

class InlineUsoMetodoPagoForm(forms.ModelForm):
    """
    adds script and custom data atribute for use as selector
    """
    class Meta:
        model = UsoMetodoPago
        fields = ["metodo", "monto", "declarado"]
        widgets = {
            'monto': UnfoldAdminTextInputWidget(attrs={'data-target':'metodo_monto_calculate_total'}),
            "metodo": UnfoldAdminSelectWidget(attrs={"style":"background-color:#f5d0fe"})  
        }

    class Media:
        js = ['admin/js/vendas_formset.js']

    
class InlineCompraVidrosForm(forms.ModelForm):
    """
    adds script and custom data atribute for use as selector
    """
    class Meta:
        fields = ["cantidad", "precio"]
        model = CompraVidros
        widgets = {
            'precio': forms.TextInput(attrs={
                'class': 'pointer-events-none bg-gray-600	border bg-white font-medium min-w-20 rounded-md shadow-sm text-gray-500 text-sm dark:bg-gray-900 dark:border-gray-700 dark:text-gray-300  dark:group-[.errors]:border-red-500  px-3 py-2 w-full max-w-2xl'
                ,"tabindex":"-1"
                , "style":"background-color:#eee"
                , "data-target" :"compravidros_precio_calculate_total"
                 
            }),
            'cantidad': UnfoldAdminIntegerFieldWidget(attrs={
                "data-target":"compravidros_cantidad_calculate_total",
                'x-on:input':'$dispatch("calculate")'
            }),  
        }

# border bg-white font-medium min-w-20 rounded-md shadow-sm text-gray-500 text-sm focus:ring focus:ring-primary-300 focus:border-primary-600 focus:outline-none group-[.errors]:border-red-600 group-[.errors]:focus:ring-red-200 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-300 dark:focus:border-primary-600 dark:focus:ring-primary-700 dark:focus:ring-opacity-50 dark:group-[.errors]:border-red-500 dark:group-[.errors]:focus:ring-red-600/40 px-3 py-2 w-full max-w-2xl
        # border bg-white font-medium min-w-20 rounded-md shadow-sm text-gray-500 text-sm focus:ring focus:ring-primary-300 focus:border-primary-600 focus:outline-none group-[.errors]:border-red-600 group-[.errors]:focus:ring-red-200 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-300 dark:focus:border-primary-600 dark:focus:ring-primary-700 dark:focus:ring-opacity-50 dark:group-[.errors]:border-red-500 dark:group-[.errors]:focus:ring-red-600/40 px-3 py-2 w-full max-w-2xl