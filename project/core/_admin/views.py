import json
import datetime
from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpRequest
from django.utils import timezone as tz
from django.utils.translation import gettext_lazy as _
from django_htmx.http import trigger_client_event

from core.models import (
    Venta,
    Producto,
    VentaItem,
    Produccion,
    Ralada,
    Periodo
)

def get_home_navegation(request):
    return  [
        {"title": _("Vendas"), "link": reverse_lazy('admin:vendas'), "active":reverse_lazy('admin:vendas') == request.path_info},
        {"title": _("Produção"), "link": reverse_lazy('admin:producao'), "active":reverse_lazy('admin:producao') == request.path_info},
    ]

def get_current_periodo_rango(request: HttpRequest) -> tuple[datetime.date, datetime.date]: 
    """
    Retrieves the date range for a period based on the 'periodo_inicio' query parameter.

    If 'periodo_inicio' is provided, it finds the corresponding 'Periodo' and returns its date range. 
    If not, it returns the date range of the most recent 'Periodo'.
    """
    if periodo_inicio := request.GET.get("periodo_inicio"):
        try:
            periodo = Periodo.objects.get(inicio=periodo_inicio)
            return periodo.rango_fechas()
        except Periodo.DoesNotExist:
            pass

    periodo = Periodo.objects.last()
    return periodo.rango_fechas()
            

def vendas(request, *args, **kwargs):
    """
    custom view for shows sales with charts
    and also sales table
    """
    table_template = "admin/components/table_ventas.html"
    year = tz.now().year
    month = tz.now().month
    
    # this is like pagination
    periodos = Periodo.objects.all() 
    start, end = get_current_periodo_rango(request=request)
    ventas = Venta.objects.filter(fecha_venta__range=[start, end])
    
    # data para graficos
    ventas_diaria_metodos = Venta.objects.grafico_bar_metodos_de_pago_diario(start=start, end=end)
    fechas_venta_diaria = ventas_diaria_metodos.pop()
    kpi = Venta.objects.kpi_totales_por_metodo(start=start, end=end)
    producto_vendido = Producto.objects.cantidad_vendida_progress_chart(start=start, end=end)
    venta_mensual_productos = VentaItem.objects.grafico_bar_montos_productos_vendidos_mensual(start=start, end=end)
    
    navegation = get_home_navegation(request)
    
    context = kwargs['context']
    custom_template = kwargs['custom_template']

    context.update(
        {
            "periodos":periodos,
            "current_periodo":start.strftime("%Y-%m-%d"),
            "table_template": table_template,
            "table_context":ventas,
            "navigation": navegation,
            "main_graphic_bar_title": "Monto de Ventas Diarias Segum Metodo de Pago",
            "kpi":kpi,
            "progress_section_title":"Produtos Vendidos por Quantidades",
            "progress": producto_vendido,
            "chart_diario": json.dumps(
                {
                    "labels": [*fechas_venta_diaria],
                    "datasets": ventas_diaria_metodos,
                    
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

    resp = render(request, custom_template, context)
    return trigger_client_event(resp, "reload_charts", after="swap")

def producao(request, *args, **kwargs):
    """
    custom view shows production related info
    and also custom production table  
    """
    table_template = "admin/components/table_produccion.html"

    year = tz.now().year
    month = tz.now().month
    
    produccion = Produccion.objects.filter(ralada__fecha_ralada__month=month, ralada__fecha_ralada__year=year)
    procesamiento = Ralada.objects.peso_y_cantidades_procesadas_kpi(year=year, month=month)
    productos_elaborados = Producto.objects.produccion_al_mes_progress_chart(year=year, month=month)
    navegation = get_home_navegation(request)
    
    context = kwargs['context']
    custom_template = kwargs['custom_template']

    context.update(
        {
            "navigation": navegation,
            "table_template": table_template,
            "table_context":produccion,
            "main_graphic_bar_title": "Vendas Diarias Segum Metodo de Pago",
            "kpi": procesamiento,
            "progress_section_title":"Produtos Produzidos No Mes",
            "progress": productos_elaborados,
        },
    )

    resp = render(request, custom_template, context)
    return trigger_client_event(resp, "reload_charts", after="swap")