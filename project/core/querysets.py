import calendar
from typing import Iterable
from collections import defaultdict
from decimal import Decimal
from django.db import models
from django.db.models.functions import Cast, Coalesce
from django.utils.safestring import mark_safe
from django.utils import timezone as tz

class VentaQueryset(models.QuerySet):  
    def kpi_totales_por_metodo(
        self,
        start: models.DateField,
        end: models.DateField,
        # year: int = tz.now().year,
        # month: int = tz.now().month,
    ) -> dict[str, Decimal]:
        """
        devuelve los totales mensuales para cada metodo de pago
        en formato para KPI
        """
        # queryset = self.filter(fecha_venta__year=year, fecha_venta__month=month)\
        queryset = self.filter(fecha_venta__range=[start, end])\
            .annotate(metodo=models.F('usos_metodo_pago__metodo__tipo'))\
            .values('metodo')\
            .annotate(total_ventas=models.Sum('usos_metodo_pago__monto', output_field=models.DecimalField()))\
            
        produccion = []
        metodos = {'P':'Vendas em Pix', 'D':'Vendas em Dinheiro', 'C':'Vendas no Cartão'}
        footers = {'P':'Vendas em Pix', 'D':'Vendas em Dinheiro', 'C':'Inclui vendas de todos os tipos de Cartão'}
        for item in queryset:
            metodo = metodos[item['metodo']]
            footer = footers[item['metodo']]

            produccion.append({
                "title":metodo,
                "metric":f"R$ {item['total_ventas']}",
                "footer": footer,
            })
        return produccion

    
    
    def grafico_bar_metodos_de_pago_diario(
        self,
        start: models.DateField,
        end: models.DateField,
        # year: int = tz.now().year,
        # month: int = tz.now().month,

    ):
        """
        totales diarios por metodo de pago
        con el formato apropiado para usar
        GRAFICO DE BARRAS en chartjs
        """

        
        # queryset = self.filter(fecha_venta__year=year, fecha_venta__month=month)\
        queryset = self.filter(fecha_venta__range=[start, end])\
            .annotate(metodo=models.F('usos_metodo_pago__metodo__tipo'))\
            .values('fecha_venta', 'metodo')\
            .annotate(total_ventas=models.Sum('usos_metodo_pago__monto', output_field=models.FloatField()))\
            .order_by('fecha_venta', 'metodo')

        # desagregating data
        fechas_set = set()
        carton = {"nombre":"Cartão", "data":[]}
        efectivo = {"nombre":"Dinheiro", "data": []}
        pix = {"nombre":"Pix", "data": []}

        # for help mapping data
        metodos = {'C':carton, 'D':efectivo, 'P':pix}

        # the value for 'metodo_pago' will be 0 by default
        ventas_por_metodo = defaultdict(lambda: {'C': 0, 'D': 0, 'P': 0})

        for venta in queryset:
            fecha = venta['fecha_venta']#.strftime('%d/%m')
            fechas_set.add(fecha)

            metodo_pago = venta['metodo'] # C || D || P
            total_ventas = venta['total_ventas']
            ventas_por_metodo[fecha][metodo_pago] = total_ventas # this works because defaultdict

        fechas_ordenadas = sorted(fechas_set)
        for fecha in fechas_ordenadas:
            for metodo in ventas_por_metodo[fecha]:
                # metodos[metodo]["data"].append([0, ventas_por_metodo[fecha][metodo]])
                metodos[metodo]["data"].append(ventas_por_metodo[fecha][metodo])

        # formating data for bar chart
        datasets = []
        background_colors = ["#f0abfc", "#9333ea", "#fb923c", "#b45309"]
        for i, metodo in enumerate([carton, efectivo, pix]):
            index = i % len(background_colors)

            datasets.append({
                "label": metodo["nombre"],
                "data":metodo["data"],
                "borderRdius":5,
                # "barThickness": 5,
                "backgroundColor":background_colors[index],
            })
        
        sales_by_method = {
            "datasets": datasets,     
            "labels": list(map(lambda d: d.strftime('%d/%m'), fechas_ordenadas)) 
        }
         # this must be pop in the view
        return sales_by_method

class VentaItemQueryset(models.QuerySet):
    def grafico_bar_montos_productos_vendidos_mensual(
        self,
        start: models.DateField,
        end: models.DateField,
        # year: int = tz.now().year,
        # month: int = tz.now().month,

    ):
        """
        total mensual vendido por producto
        con el formato apropiado para usar
        GRAFICO DE BARRAS en chartjs
        """

        queryset = self.filter(
            venta__fecha_venta__range=[start, end]
        ).annotate(
            nombre=models.F('producto__nombre'),
            monto=models.ExpressionWrapper(
                models.F('precio') * models.F('cantidad'),
                output_field=models.FloatField()
            )
        ).values('nombre')\
            .annotate(
                totales=models.Sum('monto')
            ).order_by('producto', 'totales')
        
        datasets = []

        background_colors = ["#f0abfc", "#9333ea", "#fb923c", "#b45309", "#be123c", "#ec4899", "#1d4ed8" ,"#0ea5e9", "#16a34a", "#fde047", "#444444", "#34d399"]
        for i, producto in enumerate(queryset):
            index = i % len(background_colors)
            
            datasets.append({
                "label": producto['nombre'].capitalize(),
                "data":[producto['totales']],
                "borderRdius":5,
                "barThickness": 30,
                "backgroundColor":background_colors[index],
            })
        return datasets

class ProductoQueryset(models.QuerySet):
    def produccion_al_mes_progress_chart(
        self, 
        year: int =tz.now().year,
        month: int =tz.now().month,    
    ):
        """
        cantidades producidas al mes por producto
        formato de data para PROGRESS CHART
        """
        queryset = self.filter(
            es_fabricado=True
        ).annotate(
            valor=Cast(models.F('precio'), models.FloatField())
        ).values(
            'nombre',
            'valor'
        ).annotate(
            total_producido=Coalesce(
                models.Sum(
                    'producciones__cantidad', 
                    filter=models.Q(
                        producciones__produccion__ralada__fecha_ralada__year=year, 
                        producciones__produccion__ralada__fecha_ralada__month=month
                    )
                ),
                models.Value(0)
            )
        ).order_by('tipo_guarana', '-peso', 'nombre')

        producto_mas_vendido =  max(queryset,  key=lambda p: p['total_producido'])
        cantidad_maxima = producto_mas_vendido["total_producido"] + 1

        cantidad_maxima = queryset[0]["total_producido"] + 1
        productos = []
        for item in queryset:
            value = int(item["total_producido"] / cantidad_maxima * 100) 
            
            productos.append({
                "title": f"{item['nombre'].capitalize()} R$ {item['valor']}",
                "description":f"{item['total_producido']} produtos produzidos",
                "value":value
            })
        return productos


    def cantidad_vendida_progress_chart(
        self,
        start: models.DateField,
        end: models.DateField,
        # year: int = tz.now().year,
        # month: int = tz.now().month,
    ):
        """
        cantidades vendidas al mes por producto
        formato de data para PROGRESS CHART
        """
        queryset = self.values(
            'nombre',
        ).annotate(
            cantidad_vendida=Coalesce(
                models.Sum(
                    'venta_items__cantidad', 
                    filter=models.Q(
                        venta_items__venta__fecha_venta__range=[start, end] 
                    )
                ),
                models.Value(0)
            ),
        ).order_by('tipo_guarana', '-peso', 'nombre')

        producto_mas_vendido =  max(queryset,  key=lambda p: p['cantidad_vendida'])
        cantidad_maxima = producto_mas_vendido["cantidad_vendida"] + 1
        productos = []
        for item in queryset:
            value = int(item["cantidad_vendida"] / cantidad_maxima * 100) 
            
            productos.append({
                "title": item['nombre'].capitalize(),
                "description":f"{item['cantidad_vendida']} produtos vendidos",
                "value":value
            })
        return productos
class RaladaQueryset(models.QuerySet):
    def peso_y_cantidades_procesadas_kpi(
        self, 
        year=tz.now().year,
        month=tz.now().month,
    ):
        """
        FORMATEANDO data para "kpi"
        TOTAL peso y cantidad de bastones procesados para todas las variedades
        """
        queryset =  self.filter(fecha_ralada__year=year, fecha_ralada__month=month)\
            .annotate(nombre=models.F('saco__tipo_guarana__nombre'))\
            .values('nombre')\
            .annotate(
                total_bastones=models.Sum('cantidad_bastones'),
                total_peso=Cast(models.Sum('peso_inicial'), models.FloatField()) / 1000
        )
        produccion = []   
        for item in queryset:
            produccion.append({
                "title":item["nombre"].title(),
                "metric":f"{item['total_bastones']} Bastões Procesados",
                "footer": f"Tem se proccesado {item['total_peso']} kg do {item['nombre']}"
            })
        return produccion
