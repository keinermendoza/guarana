from decimal import Decimal, ROUND_CEILING
from typing import Any, Dict
from django.db.models import Model
from django import forms
from django.forms import Form
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.urls import path
from django.shortcuts import render
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from unfold.contrib.inlines.admin import NonrelatedTabularInline
from unfold.decorators import display
from unfold.admin import ModelAdmin, TabularInline, StackedInline

from .models import (
    TipoGuarana,
    Saco,
    MetodoPago,
    UsoMetodoPago,
    Periodo,
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
    AnotacionInventario,
)

from ._admin.views import (
    producao,
    vendas,
)

from ._admin.forms import (
    VentaForm,
    InlineRaladaForm,
    InlineVentaItemAddForm,
    InlineUsoMetodoPagoForm,
    ProduccionForm,
    InlineCompraVidrosForm,
    InlineProduccionDetalleForm,
    RaladaInlineFormset,
    ProduccionDetalleFormset,
    InlineUsoMetodoPagoFormset,
    InlineVentaItemFormset,
)


@admin.register(CompraVidros)
class CompraVidrosAdmin(ModelAdmin):
    pass

@admin.register(Periodo)
class PeriodoAdmin(ModelAdmin):
    pass


@admin.register(UsoMetodoPago)
class UsoMetodoPagoAdmin(ModelAdmin):
    list_display = [
        "fecha_venta",
        "monto",
        "metodo",
        "detalle_compra",
        "calculo",
        "declarado",
    ]
    list_display_links = None
    actions = ["declarar_pago", "retirar_declaracion"]
    list_filter = ["venta__fecha_venta", "metodo__tipo"]
    ordering = ["venta__fecha_venta", "venta__pk"]

    @display(description="data")
    def fecha_venta(self, obj):
        if obj.venta.fecha_venta:
            return obj.venta.fecha_corta
        return ""

    @display(description="detalhe")
    def detalle_compra(self, obj) -> str:
        items = obj.venta.items.all()
        items_list = [f"{item.cantidad} de {item.precio}" for item in items]
        venta_nota = obj.venta.nota if obj.venta.nota else ""
        return ", ".join(items_list) + " " + venta_nota

    @display(description="Calculo")
    def calculo(self, obj):
        decimals = 3
        result = obj.monto / 170
        result = result.quantize(Decimal(f'1.{"0" * decimals}'), rounding=ROUND_CEILING)
        return result

    @admin.action(description="Marcar pagamento como declarado")
    def declarar_pago(modeladmin, request, queryset):
        queryset.update(declarado=True)

    @admin.action(description="Marcar pagamento como NÃO declarado")
    def retirar_declaracion(modeladmin, request, queryset):
        queryset.update(declarado=False)


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
            path(
                "vendas/", self.admin_site.admin_view(self.vendas_view), name="vendas"
            ),
            path(
                "producao/",
                self.admin_site.admin_view(self.producao_view),
                name="producao",
            ),
            path("test/", self.admin_site.admin_view(self.test), name="test"),
        ]
        return my_urls + urls

    def test(self, request, *args, **kwargs):
        context = self.admin_site.each_context(request)
        context["table_context"] = Venta.objects.all()
        return render(request, "admin/components/table_ventas.html", context)

    def vendas_view(self, request, *args, **kwargs):
        context = self.admin_site.each_context(request)
        kwargs["context"] = context
        kwargs["custom_template"] = self.custom_template
        return vendas(request, *args, **kwargs)

    def producao_view(self, request, *args, **kwargs):
        context = self.admin_site.each_context(request)
        kwargs["context"] = context
        kwargs["custom_template"] = self.custom_template
        return producao(request, *args, **kwargs)


@admin.register(AnotacionInventario)
class AnotacionInventarioAdmin(ModelAdmin):
    pass


@admin.register(TipoGuarana)
class TipoGuaranaAdmin(ModelAdmin):
    pass


@admin.register(MetodoPago)
class MetodoPagoAdmin(ModelAdmin):
    # search_fields = ["nombre"]
    pass


@admin.register(Saco)
class SacoAdmin(ModelAdmin):
    list_display = ["__str__", "tipo_guarana"]

    def get_urls(self):
        """
        adds customs urls and views for handeling upload/delete related images
        """
        urls = super().get_urls()
        my_urls = [
            path(
                "update_product_options/",
                self.admin_site.admin_view(self.update_product_options),
                name="update_product_options",
            ),
        ]
        return my_urls + urls

    def update_product_options(self, request, *args, **kwargs):
        partial_template = "admin/forms/produccion_detalle_producto_options.html"
        saco_id = request.GET.get("saco")
        try:
            saco = Saco.objects.get(id=saco_id)
            productos = Producto.objects.filter(
                es_fabricado=True, tipo_guarana=saco.tipo_guarana
            )
        except Saco.DoesNotExist:
            productos = []

        return render(request, partial_template, {"productos": productos})


@admin.register(Producto)
class ProductoAdmin(ModelAdmin):
    search_fields = ["nombre"]
    list_display = ["nombre", "peso", "precio", "tipo_guarana"]


class RaladaInline(StackedInline):
    model = Ralada
    form = InlineRaladaForm
    formset = RaladaInlineFormset
    tab = True


class ProduccionDetalleInline(TabularInline):
    formset = ProduccionDetalleFormset
    form = InlineProduccionDetalleForm
    model = ProduccionDetalle


@admin.register(Produccion)
class ProduccionAdmin(ModelAdmin):
    # change template for extend from custom base.html that uses custom templatetag
    change_form_template = "admin/ralada_change_form.html"
    form = ProduccionForm

    inlines = [RaladaInline, ProduccionDetalleInline]

    readonly_fields = ["fecha_registro"]
    list_display = ["__str__", "consumo", "numero_ralada", "fecha_ralada"]
    search_fields = ["nota"]

    @display(description="N° Ralada", label=True)
    def numero_ralada(self, obj):
        return f"{obj.ralada.numero}"

    @display(description="Fecha Ralada")
    def fecha_ralada(self, obj):
        return f"{obj.ralada.fecha_ralada}"

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """
        add context for change template render by templatetag tab_list.
        tab_list is loaded in base.html
        reads the context and renders tab_list.html passing some of the context
        """
        extra_context = extra_context or {}
        extra_context.update({"put_first_ralada_tab": True})
        return super().changeform_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )


class VentaItemInline(TabularInline):
    model = VentaItem
    form = InlineVentaItemAddForm
    formset = InlineVentaItemFormset
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        producto = formset.form.base_fields["producto"]
        producto.widget.can_add_related = producto.widget.can_change_related = (
            producto.widget.can_delete_related
        ) = producto.widget.can_view_related = False
        return formset


class UsoMetodoPagoInline(TabularInline):
    model = UsoMetodoPago
    # autocomplete_fields = ["metodo"]
    extra = 1
    form = InlineUsoMetodoPagoForm
    formset = InlineUsoMetodoPagoFormset

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        metodo = formset.form.base_fields["metodo"]
        metodo.widget.can_add_related = metodo.widget.can_change_related = (
            metodo.widget.can_delete_related
        ) = metodo.widget.can_view_related = False
        return formset


class CompraVidrosInline(TabularInline):
    form = InlineCompraVidrosForm
    model = CompraVidros
    extra = 1


@admin.register(Venta)
class VentaAdmin(ModelAdmin):
    form = VentaForm
    list_display = ["__str__", "metodos_de_pago", "detalle_venta"]
    list_filter = ["fecha_venta", "usos_metodo_pago__metodo__tipo"]
    ordering = ["fecha_venta", "pk"]
    inlines = [VentaItemInline, UsoMetodoPagoInline, CompraVidrosInline]
    fieldsets = (
        ("Venta", {"classes": ["tab"], "fields": ["total", "fecha_venta"]}),
        (
            "Extras",
            {
                "classes": ["tab"],
                "fields": ["nota"],
            },
        ),
    )

    @display(description="detalhe da venda")
    def detalle_venta(self, obj) -> str:
        items = obj.items.all()
        items_list = [f"{item.cantidad} de {item.precio}" for item in items]
        venta_nota = obj.nota if obj.nota else ""
        return ", ".join(items_list) + " " + venta_nota

    @display(description="monto pago por forma de pagamento")
    def metodos_de_pago(self, obj):
        usos_metodos = obj.usos_metodo_pago.all()
        usos_metodos_list = [
            f"{uso_metodo.metodo.nombre} x R$ {uso_metodo.monto}"
            for uso_metodo in usos_metodos
        ]
        return ", ".join(usos_metodos_list)

    def get_form(self, request, obj=None, change=False, **kwargs):

        formsets, inline_instances = self._create_formsets(
            request,
            obj,
            change=change,
        )
        DefaultClassForm = super().get_form(request, obj, **kwargs)

        class RequestForm(DefaultClassForm):
            def __new__(cls, *args, **kwargs):
                kwargs["request"] = request
                kwargs["formsets"] = formsets
                return DefaultClassForm(*args, **kwargs)

        return RequestForm
