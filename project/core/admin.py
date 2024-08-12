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

from .views import get_extra_context

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
            path("diario/", self.admin_site.admin_view(self.resumen_diario), name='resumen_diario'),
            path("semanal/", self.admin_site.admin_view(self.resumen_semanal), name='resumen_semanal'),
            path("mensal/", self.admin_site.admin_view(self.resumen_mensual), name='resumen_mensual'),

        ]
        return my_urls + urls
    

    def resumen_diario(self, request, *args, **kwargs):
        """
        custom view for show daily amounts
        """

        data_ventas = Venta.objects.data_for_chartjs()
        context = self.admin_site.each_context(request)
        context.update(
            {
                "navigation": [
                    {"title": _("Hoje"), "link": reverse_lazy('admin:resumen_diario'), "active":reverse_lazy('admin:resumen_diario') == request.path_info},
                    {"title": _("Semana"), "link": reverse_lazy('admin:resumen_semanal'), "active":reverse_lazy('admin:resumen_semanal') == request.path_info},
                    {"title": _("Mes"), "link": reverse_lazy('admin:resumen_mensual'), "active":reverse_lazy('admin:resumen_mensual') == request.path_info},
                ],
                "filters": [
                    {"title": _("All"), "link": "#", "active": True},
                    {
                        "title": _("New"),
                        "link": "#",
                    },
                ],
                "kpi": [
                    {
                        "title": "Product A Performance",
                        "metric": "$1,234.56",
                        "footer": mark_safe(
                            '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                        ),
                        # "chart": json.dumps(
                        #     {
                        #         "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                        #         "datasets": [{"data": average, "borderColor": "#9333ea"}],
                        #     }
                        # ),
                    },
                    {
                        "title": "Product B Performance",
                        "metric": "$1,234.56",
                        "footer": mark_safe(
                            '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                        ),
                    },
                    {
                        "title": "Product C Performance",
                        "metric": "$1,234.56",
                        "footer": mark_safe(
                            '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                        ),
                    },
                ],
                # "progress": [
                #     {
                #         "title": "Social marketing e-book",
                #         "description": " $1,234.56",
                #         "value": random.randint(10, 90),
                #     },
                #     {
                #         "title": "Freelancing tasks",
                #         "description": " $1,234.56",
                #         "value": random.randint(10, 90),
                #     },
                #     {
                #         "title": "Development coaching",
                #         "description": " $1,234.56",
                #         "value": random.randint(10, 90),
                #     },
                #     {
                #         "title": "Product consulting",
                #         "description": " $1,234.56",
                #         "value": random.randint(10, 90),
                #     },
                #     {
                #         "title": "Other income",
                #         "description": " $1,234.56",
                #         "value": random.randint(10, 90),
                #     },
                # ],
                "chart": json.dumps(
                    {
                        "labels": data_ventas['fechas'],
                        "datasets": [
                            {
                                "label": "Dinheiro",
                                "data": data_ventas['efectivo'],
                                "borderRadius":5,
                                "barThickness": 10,
                                "backgroundColor": "#f0abfc",
                            },
                            {
                                "label": "Cartão",
                                "data": data_ventas['carton'],
                                "borderRadius":5,
                                "barThickness": 10,
                                "backgroundColor": "#9333ea",
                            },
                            {
                                "label": "Pix",
                                "data": data_ventas['pix'],
                                "borderRadius":5,
                                "barThickness": 10,
                                "backgroundColor": "#f43f5e",
                            },
                        ],
                    }
                ),
                "performance": [
                    {
                        "title": _("Last week revenue"),
                        "metric": "$1,234.56",
                        "footer": mark_safe(
                            '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                        ),
                        # "chart": json.dumps(
                        #     {
                        #         "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                        #         "datasets": [
                        #             {"data": performance_positive, "borderColor": "#9333ea"}
                        #         ],
                        #     }
                        # ),
                    },
                    {
                        "title": _("Last week expenses"),
                        "metric": "$1,234.56",
                        "footer": mark_safe(
                            '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                        ),
                        # "chart": json.dumps(
                        #     {
                        #         "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                        #         "datasets": [
                        #             {"data": performance_negative, "borderColor": "#f43f5e"}
                        #         ],
                        #     }
                        # ),
                    },
                ],
            },
        )

        resp = render(request, self.custom_template, context)
        return trigger_client_event(resp, "reload_charts", after="swap")
    def resumen_semanal(self, request, *args, **kwargs):
        """
        custom view for show daily amounts
        """
        context = self.admin_site.each_context(request)
        context = get_extra_context(request, context)
        resp = render(request, self.custom_template, context)
        return trigger_client_event(resp, "reload_charts", after="swap")
    def resumen_mensual(self, request, *args, **kwargs):
        """
        custom view for show daily amounts
        """
        context = self.admin_site.each_context(request)
        context = get_extra_context(request, context)
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


    