import random

from django import forms
from django.db import models
from django.urls import path
from django.shortcuts import render
from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from unfold.contrib.inlines.admin import NonrelatedTabularInline
from django.utils import timezone
from django.utils.formats import date_format
from django_htmx.http import trigger_client_event


from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
import json
from django.urls import reverse_lazy

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
    CompraVidros,
    Consumo,
    Gasto,
    Inventario,
    AnotacionInventario 
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

# from .views import get_extra_context

def get_home_navegation(request):
    return  [
        {"title": _("Vendas"), "link": reverse_lazy('admin:vendas'), "active":reverse_lazy('admin:vendas') == request.path_info},
        {"title": _("Produção"), "link": reverse_lazy('admin:producao'), "active":reverse_lazy('admin:producao') == request.path_info},
    ]
    
    


@admin.register(CompraVidros)
class CompraVidrosAdmin(ModelAdmin):
   pass

@admin.register(UsoMetodoPago)
class UsoMetodoPagoAdmin(ModelAdmin):
   list_display = ["monto", "fecha_venta", "metodo", "declarado"]
   list_display_links = None
   
   @display(description="data")
   def fecha_venta(self, obj):
       if obj.venta.fecha_venta:
            return date_format(timezone.localtime(obj.venta.fecha_venta), use_l10n=True)
       return ""

@admin.register(Consumo)
class ConsumoAdmin(ModelAdmin):
   pass

@admin.register(Gasto)
class GastoAdmin(ModelAdmin):
   pass


@admin.register(Inventario)
class InventarioAdmin(ModelAdmin):
    custom_template = "admin/admin_home_partials/main_content.html"
            
    def get_urls(self):
        """
        adds customs urls and views for handeling upload/delete related images
        """
        urls = super().get_urls()
        my_urls = [
            path("vendas/", self.admin_site.admin_view(self.vendas), name='vendas'),
            path("producao/", self.admin_site.admin_view(self.producao), name='producao'),
            path("mensal/", self.admin_site.admin_view(self.resumen_mensual), name='resumen_mensual'),

        ]
        return my_urls + urls
    

    def vendas(self, request, *args, **kwargs):
        """
        custom view for show daily amounts
        """
        table_template = "admin/components/table_ventas.html"
        year = 2024
        month = 8

        ventas = Venta.objects.all()
       
        # data para graficos
        ventas_diaria_metodos = Venta.objects.grafico_bar_metodos_de_pago_diario(year=year, month=month)
        totales = Venta.objects.kpi_stats_totales_por_metodo(year=year, month=month)
        # producto_vendido = Producto.objects.cantidad_vendida_bar_chart(year=year, month=month)
        venta_mensual_productos = VentaItem.objects.grafico_bar_montos_productos_vendidos_mensual(year=year, month=month)
        cantidad_total_por_productos = VentaItem.objects.progress_chart_cantidad_total_por_productos(year=year, month=month)
        
        navegation = get_home_navegation(request)
        
        context = self.admin_site.each_context(request)
        context.update(
            {
                "table_template": table_template,
                "table_context":ventas,
                "navigation": navegation,
                "main_graphic_bar_title": "Monto de Ventas Diarias Segum Metodo de Pago",
                "kpi": [
                    {
                        "title": "Vendas no Cartão",
                        "metric": f"R${totales['carton']}",
                        "footer": mark_safe(
                            '<strong class="text-green-600 font-medium">Inclui vendas de todos os tipos de Cartão</strong>'
                        ),
                    },
                    {
                        "title": "Vendas em Dinheiro",
                        "metric": f"R${totales['efectivo']}",
                        "footer": mark_safe(
                            '<strong class="text-green-600 font-medium">Vendas em Dinheiro</strong>'
                        ),
                    },
                    {
                        "title": "Vendas em Pix",
                        "metric": f"R${totales['efectivo']}",
                        "footer": mark_safe(
                            '<strong class="text-green-600 font-medium">Vendas em Pix</strong>'
                        ),
                    },
                ],
                "progress_section_title":"Produtos Vendidos por Quantidades",
                "progress": [
                    *cantidad_total_por_productos
                ],
                "chart_diario": json.dumps(
                    {
                        "labels": ventas_diaria_metodos['fechas'],
                        "datasets": [
                            {
                                "label": "Dinheiro",
                                "data": ventas_diaria_metodos['efectivo'],
                                "borderRadius":5,
                                "barThickness": 10,
                                "backgroundColor": "#f0abfc",
                            },
                            {
                                "label": "Cartão",
                                "data": ventas_diaria_metodos['carton'],
                                "borderRadius":5,
                                "barThickness": 10,
                                "backgroundColor": "#9333ea",
                            },
                            {
                                "label": "Pix",
                                "data": ventas_diaria_metodos['pix'],
                                "borderRadius":5,
                                "barThickness": 10,
                                "backgroundColor": "#f43f5e",
                            },
                        ],
                    }
                ),
                "chart_mensual_title": f"Monto Vendido por Produto no mes",
                "chart_mensual": json.dumps(
                    {
                        "labels": [f"Mes {month}"],
                        "datasets": venta_mensual_productos,
                    }
                )
               
            },
        )

        resp = render(request, self.custom_template, context)
        return trigger_client_event(resp, "reload_charts", after="swap")
    
    def producao(self, request, *args, **kwargs):
        """
        custom view for show daily amounts
        """
        year = 2024
        month = 8
        produccion = Ralada.objects.peso_y_cantidades_procesadas_kpi(year=year, month=7)
        produccion_mensual = Producto.objects.produccion_al_mes_progress_chart(year=year, month=7)
        navegation = get_home_navegation(request)
        
        context = self.admin_site.each_context(request)
        context.update(
            {
                "navigation": navegation,
                "main_graphic_bar_title": "Vendas Diarias Segum Metodo de Pago",
                "kpi": produccion,
                "progress_section_title":"Produtos Produzidos No Mes",
                "progress": produccion_mensual,
            },
        )

        resp = render(request, self.custom_template, context)
        return trigger_client_event(resp, "reload_charts", after="swap")
    
    def resumen_mensual(self, request, *args, **kwargs):
        """
        custom view for show daily amounts
        """
        context = self.admin_site.each_context(request)
        resp = render(request, self.custom_template, context)
        return trigger_client_event(resp, "reload_charts", after="swap")
@admin.register(AnotacionInventario)
class AnotacionInventarioAdmin(ModelAdmin):
   pass



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
    extra = 1

class UsoMetodoPagoInline(TabularInline):
    model = UsoMetodoPago
    extra = 1
    form = InlineUsoMetodoPagoForm

class CompraVidrosInline(NonrelatedTabularInline):
    model = CompraVidros
    fields = ["precio", "cantidad"]
    extra = 1

    def get_form_queryset(self, obj):
        """
        Gets all nonrelated objects needed for inlines. Method must be implemented.
        """
        return self.model.objects.all()

    def save_new_instance(self, parent, instance):
        """
        Extra save method which can for example update inline instances based on current
        main model object. Method must be implemented.
        """
        pass

@admin.register(Venta)
class VentaAdmin(ModelAdmin):
    inlines = [UsoMetodoPagoInline, VentaItemInline, CompraVidrosInline]

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


    