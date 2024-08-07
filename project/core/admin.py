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

@admin.register(Ralada)
class RaladaAdmin(ModelAdmin):
    pass

class ProduccionDetalleInline(TabularInline):
    model = ProduccionDetalle

@admin.register(Produccion)
class ProduccionAdmin(ModelAdmin):
    inlines = [ProduccionDetalleInline]

class VentaItemInline(TabularInline):
    model = VentaItem

@admin.register(Venta)
class VentaAdmin(ModelAdmin):
    inlines = [VentaItemInline]
