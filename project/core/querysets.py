from typing import Iterable
from collections import defaultdict
from decimal import Decimal
from django.db import models
from django.db.models.functions import Cast

from django.utils import timezone as tz

# referencia MetodoPago.Tipos en models
METODO_PAGO_PIX = "P"
METODO_PAGO_EFECTIVO = "D"
METODO_PAGO_CARTON = "C"


class VentaQueryset(models.QuerySet):
    def venta_diaria(
        self,
        year: int = tz.now().year,
        month: int = tz.now().month,
    ) -> dict[str, list[Decimal | str]]:
        """
        regresa el total vendido en un diccionario de listas
        las keys son los tipos de metodos
        los items de las listas representan la venta total diaria 
        """
        
        fechas = []
        efectivo = []
        pix = []
        carton = []

        # Crear un set para rastrear las fechas únicas
        fechas_set = set()

        # Inicializar un diccionario para almacenar las ventas por fecha y método de pago
        ventas_por_metodo = defaultdict(lambda: {METODO_PAGO_EFECTIVO: 0, METODO_PAGO_PIX: 0, METODO_PAGO_CARTON: 0})
        ventas = self.venta_mensual_por_dia_y_metodo_pago(year=year, month=month)

        # Recorrer las ventas y llenar el diccionario
        for venta in ventas:
            fecha = venta['fecha_venta'].strftime('%d/%m')
            metodo_pago = venta['metodo_pago__tipo']
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
        return {
            "fechas": fechas,
            "efectivo": efectivo,
            "pix": pix,
            "carton": carton
        }
    
    def totales_mensuales(
        self,
        year: int = tz.now().year,
        month: int = tz.now().month
    ) -> dict[str, Decimal]:
        """
        devuelve los totales mensuales
        """
        
        totales = self.venta_diaria(year=year, month=month)

        carton = sum(totales["carton"])
        efectivo = sum(totales["efectivo"])
        pix = sum(totales["pix"])

        return {
            'carton': carton,
            'efectivo':efectivo,
            'pix': pix
        }
    
    def data_grafico_bar_chartjs(
        self,
        year: int = tz.now().year,
        month: int = tz.now().month 
    ):
        """
        regresa la data con el formato apropiado para usar
        grafico de barras en chartjs
        """
        totales = self.venta_diaria(year=year, month=month)
        carton = [[0, float(i)] for i in totales["carton"]]
        efectivo = [[0, float(i)] for i in totales["efectivo"]]
        pix = [[0, float(i)] for i in totales["pix"]]

        return {
            'carton': carton,
            'efectivo':efectivo,
            'pix': pix,
            'fechas': totales['fechas']
        }

    def venta_mensual_por_dia_y_metodo_pago(
        self, 
        year: int,
        month: int,
    ) -> models.QuerySet[dict]:
        """
        filtra las ventas por mes y año.
        devuelve el total vendido diariamente por tipo de metodo de pago 
        """
        return self.filter(fecha_venta__year=year, fecha_venta__month=month)\
             .values('fecha_venta', 'metodo_pago__tipo')\
             .annotate(total_ventas=models.Sum('total', output_field=models.DecimalField()))\
             .order_by('fecha_venta', 'metodo_pago__tipo')

# class ProduccionQueryset(models.QuerySet):
#     def filtrar_por_fecha_y_tipo(
#         self, 
#         year=tz.now().year,
#         month=tz.now().month,
#         variedad="luzeia",
#     ):
#         return self.filter(fecha_venta__year=year, fecha_venta__month=month)\
#         .values('fecha_venta', 'metodo_pago__tipo')\
#         .annotate(total_ventas=models.Sum('total', output_field=models.DecimalField()))\
#         .order_by('fecha_venta', 'metodo_pago__tipo')

    

class RaladaQueryset(models.QuerySet):
    def filtrar_por_fecha_y_tipo(
        self, 
        year=tz.now().year,
        month=tz.now().month,
        variedad="luzeia",
    ):
        """
        filtra las raladas por mes, año y variedad.
        dia: anota una version corta de la fecha 
        """
        return self.filter(saco__tipo_guarana__nombre__iexact=variedad, fecha_ralada__year=year, fecha_ralada__month=month)
   
    #MEJORAR
    def bastones_diarios(
        self, 
        year=tz.now().year,
        month=tz.now().month,
        variedad="luzeia",
    ):
        """
        lista con cantidad de bastones procesados diarios
        para un mes, año y variedad  
        """
        return self.filtrar_por_fecha_y_tipo(year=year, month=month, variedad=variedad)\
            .values('fecha_ralada')\
            .annotate(total_bastones=models.Sum('cantidad_bastones'))\
            .order_by('fecha_ralada')
    #MEJORAR
    def procesado_diario(
        self,
        year=tz.now().year,
        month=tz.now().month,
        variedad="luzeia",
    ):
        """
        lista kg de guarana bastones procesado diario
        para un mes, año y variedad  
        """
        return self.filtrar_por_fecha_y_tipo(year=year, month=month, variedad=variedad)\
            .values('fecha_ralada')\
            .annotate(kg_procesados=Cast(models.Sum('peso_inicial'), models.FloatField()) / 1000)\
            .order_by('fecha_ralada')
