from typing import Iterable
from collections import defaultdict
from decimal import Decimal
from django.db import models
from django.db.models.functions import Cast, Coalesce
from django.utils.safestring import mark_safe
from django.utils import timezone as tz

# referencia MetodoPago.Tipos en models
METODO_PAGO_PIX = "P"
METODO_PAGO_EFECTIVO = "D"
METODO_PAGO_CARTON = "C"


class VentaQueryset(models.QuerySet):

    # TODO: DELETE
    def cobros_en_ventas_segun_metodo_de_pago(
        self, 
        year: int,
        month: int,
    ) -> models.QuerySet[dict]:
        """
        cobros en ventas segun metodos de pago
        Nota: en ocaciones una venta se relaiza con mas de un metodo de pago
        HELPER para funciones:
        - kpi_stats_totales_por_metodo
        - grafico_bar_metodos_de_pago_diario

        """
        queryset = self.filter(fecha_venta__year=year, fecha_venta__month=month)\
            .annotate(metodo=models.F('usos_metodo_pago__metodo__tipo'))\
            .values('fecha_venta', 'metodo')\
            .annotate(total_ventas=models.Sum('usos_metodo_pago__monto', output_field=models.DecimalField()))\
            .order_by('fecha_venta', 'metodo')

        fechas = []
        efectivo = []
        pix = []
        carton = []

        # Crear un set para rastrear las fechas únicas
        fechas_set = set()

        # Inicializar un diccionario para almacenar las ventas por fecha y método de pago
        ventas_por_metodo = defaultdict(lambda: {METODO_PAGO_EFECTIVO: 0, METODO_PAGO_PIX: 0, METODO_PAGO_CARTON: 0})

        # Recorrer las ventas y llenar el diccionario
        for venta in queryset:
            fecha = venta['fecha_venta'].strftime('%d/%m')
            metodo_pago = venta['metodo']
            total_ventas = venta['total_ventas']

            # Añadir la fecha al set de fechas
            fechas_set.add(fecha)

            # key metodo_pago es provista por defaultdict
            ventas_por_metodo[fecha][metodo_pago] = total_ventas

        # Ordenar las fechas
        fechas_ordenadas = sorted(fechas_set)

        # Llenar las listas para efectivo, pix y carton
        for fecha in fechas_ordenadas:
            fechas.append(fecha)
            efectivo.append(ventas_por_metodo[fecha][METODO_PAGO_EFECTIVO])
            pix.append(ventas_por_metodo[fecha][METODO_PAGO_PIX])
            carton.append(ventas_por_metodo[fecha][METODO_PAGO_CARTON])

        # Crear el diccionario final
        ventas =  {
            "fechas": fechas,
            "efectivo": efectivo,
            "pix": pix,
            "carton": carton
        }

        return ventas
    
    # TODO: CREATE DEDICATE METHOD
    def kpi_stats_totales_por_metodo(
        self,
        year: int = tz.now().year,
        month: int = tz.now().month
    ) -> dict[str, Decimal]:
        """
        devuelve los totales mensuales para cada metodo de pago
        en formato para KPI
        """
        
        totales = self.cobros_en_ventas_segun_metodo_de_pago(year=year, month=month)

        carton = sum(totales["carton"])
        efectivo = sum(totales["efectivo"])
        pix = sum(totales["pix"])

        return {
            'carton': carton,
            'efectivo':efectivo,
            'pix': pix
        }
    
    # TODO: CREATE DEDICATE METHOD
    def grafico_bar_metodos_de_pago_diario(
        self,
        year: int = tz.now().year,
        month: int = tz.now().month 
    ):
        """
        totales diarios por metodo de pago
        con el formato apropiado para usar
        GRAFICO DE BARRAS en chartjs
        """
        totales = self.cobros_en_ventas_segun_metodo_de_pago(year=year, month=month)
        carton = [[0, float(i)] for i in totales["carton"]]
        efectivo = [[0, float(i)] for i in totales["efectivo"]]
        pix = [[0, float(i)] for i in totales["pix"]]

        return {
            'carton': carton,
            'efectivo':efectivo,
            'pix': pix,
            'fechas': totales['fechas']
        }

    

class VentaItemQueryset(models.QuerySet):
    def grafico_bar_montos_productos_vendidos_mensual(
        self,
        year: int = tz.now().year,
        month: int = tz.now().month 
    ):
        """
        total mensual vendido por producto
        con el formato apropiado para usar
        GRAFICO DE BARRAS en chartjs
        """

        queryset = self.filter(
            venta__fecha_venta__year=year,
            venta__fecha_venta__month=month
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

        background_colors = ["#f0abfc", "#9333ea", "#f43f5e"]
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
        ).order_by('-total_producido', 'nombre')

        cantidad_maxima = queryset[0]["total_producido"] + 1
        productos = []
        for item in queryset:
            value = int(item["total_producido"] / cantidad_maxima * 100) 
            
            productos.append({
                "title": f"{item['nombre'].capitalize()} R$ {item['valor']}",
                "description":f"{item['total_producido']} produtos produzidos",
                "value":value
            })
        return sorted(productos, key=lambda x: x['title'])


    def cantidad_vendida_progress_chart(
        self,
        year: int =tz.now().year,
        month: int =tz.now().month,   
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
                        venta_items__venta__fecha_venta__year=year, 
                        venta_items__venta__fecha_venta__month=month
                    )
                ),
                models.Value(0)
            ),
        ).order_by('-cantidad_vendida', 'nombre')

        cantidad_maxima = queryset[0]["cantidad_vendida"] + 1
        productos = []
        for item in queryset:
            value = int(item["cantidad_vendida"] / cantidad_maxima * 100) 
            
            productos.append({
                "title": item['nombre'].capitalize(),
                "description":f"{item['cantidad_vendida']} produtos vendidos",
                "value":value
            })
        return sorted(productos, key=lambda x: x['title'])

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
                "footer": mark_safe(f'<strong class="text-green-600 font-medium">Tem se proccesado {item["total_peso"]} kg do {item["nombre"]} neste Mes</strong>')
            })
        return produccion
