from django import forms
from django.db import models
from django.contrib import admin
from .models import (
    TipoGuarana,
    Saco,
    MetodoPago,
    Producto,
    Ralada,
    Produccion,
    ProduccionDetalle,
    Venta,
    VentaItem,
)

from .admin_forms import InlineRaladaForm, InlineVentaItemAddForm
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
    change_form_template = "admin/change_form.html"
    fieldsets = (
        ("Producción", {
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

    # def change_view(self, request, object_id, form_url="", extra_context=None):
        """
        adds the endpoints for handle upload/delete related images to context
        in the custom 'change_form_template' 
        this scripts are loadded by 'js/admin.js'
        """
        extra_context = extra_context or {}
        extra_context.update({
            "put_first_ralada_tab": True
        })
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



@admin.register(Venta)
class VentaAdmin(ModelAdmin):
    filter_horizontal = ["metodo_pago"]
    inlines = [VentaItemInline]

    fieldsets = (
        ("Venta", {
            'fields': ('total', 'metodo_pago')
        }),
        ('Extras', {
            'fields': ['fecha_venta', 'nota'],
            'classes': ('collapse',)
        }),
    )
