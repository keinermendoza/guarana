from django import forms
from django.db import models
from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin

from .models import (
    TipoGuarana,
    Saco,
    MetodoPago,
    UsoMetodoPago,
    Producto,
    Ralada,
    Produccion,
    ProduccionDetalle,
    Venta,
    VentaItem,
)

from .admin_forms import (
    InlineRaladaForm,
    InlineVentaItemAddForm,
    InlineUsoMetodoPagoForm
) 

from unfold.decorators import display
from unfold.admin import (
    ModelAdmin,
    TabularInline,
    StackedInline
) 



@admin.register(TipoGuarana)
class TipoGuaranaAdmin(ModelAdmin):
   pass

@admin.register(MetodoPago)
class MetodoPagoAdmin(ModelAdmin):
    pass

@admin.register(Saco)
class SacoAdmin(ModelAdmin):
    list_display = ["__str__", "tipo_guarana"]


@admin.register(Producto)
class ProductoAdmin(ModelAdmin):
    search_fields = ["nombre"]
    list_display = ["__str__", "precio"]

class RaladaInline(StackedInline):
    model = Ralada
    form = InlineRaladaForm
    tab = True

class ProduccionDetalleInline(TabularInline):
    model = ProduccionDetalle
    autocomplete_fields = ["producto"]

    

@admin.register(Produccion)
class ProduccionAdmin(ModelAdmin):
    # change template for extend from custom base.html that uses custom templatetag 
    change_form_template = "admin/ralada_change_form.html"
    fieldsets = (
        ("Producción", {
            "classes": ["tab"],
            'fields': ('consumo', 'nota')
        }),
    )
  
    inlines = [RaladaInline, ProduccionDetalleInline]

    readonly_fields = ['fecha_registro']
    list_display = ['__str__', 'consumo', "numero_ralada" ,'fecha_registro']
    search_fields = ['nota']


    @display(description="N° Ralada", label=True)
    def numero_ralada(self, obj):
        return f"{obj.ralada.numero}"

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """
        add context for change template render by templatetag tab_list.
        tab_list is loaded in base.html 
        reads the context and renders tab_list.html passing some of the context
        """
        extra_context = extra_context or {}
        # extra_context.update({
        #     "put_first_ralada_tab": True
        # })
        return super().changeform_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )
    
    

class VentaItemInline(TabularInline):
    model = VentaItem
    autocomplete_fields = ["producto"]
    form = InlineVentaItemAddForm
    extra = 1

class UsoMetodoPagoInline(TabularInline):
    model = UsoMetodoPago
    extra = 1
    form = InlineUsoMetodoPagoForm

@admin.register(Venta)
class VentaAdmin(ModelAdmin):
    inlines = [UsoMetodoPagoInline, VentaItemInline]

    fieldsets = (
        ("Venta", {
            "classes": ["tab"],
            'fields': ['total']
        }),
        ('Extras', {
            "classes": ["tab"],
            'fields': ['fecha_venta', 'nota'],
        }),
    )


    