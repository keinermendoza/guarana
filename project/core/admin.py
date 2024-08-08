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

from .admin_forms import InlineRaladaForm

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
    pass

@admin.register(Producto)
class ProductoAdmin(ModelAdmin):
    pass

class RaladaInline(StackedInline):
    model = Ralada
    form = InlineRaladaForm
    tab = True

class ProduccionDetalleInline(TabularInline):
    model = ProduccionDetalle
    

@admin.register(Produccion)
class ProduccionAdmin(ModelAdmin):
    fieldsets = (
        ("Producción", {
            'fields': ('consumo', 'nota')
        }),
    )
  
    inlines = [RaladaInline, ProduccionDetalleInline]

    readonly_fields = ('fecha_registro',)

    list_display = ('__str__', 'consumo', 'fecha_registro')
    search_fields = ('nota',)
    
    

class VentaItemInline(TabularInline):
    model = VentaItem

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
