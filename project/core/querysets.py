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
        ventas =  {
            "fechas": fechas,
            "efectivo": efectivo,
            "pix": pix,
            "carton": carton
        }

        return ventas
    
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

class VentaItemQueryset(models.QuerySet):
    def queryset_cantidad_total_por_productos(
        self, 
        year: int =tz.now().year,
        month: int =tz.now().month,
    ):
        return self.filter(
            venta__fecha_venta__year=year,
            venta__fecha_venta__month=month,
            producto__es_fabricado=True
        ).values(
            'producto__nombre',
        ).annotate(cantidad_vendida=models.Sum('cantidad'))\
        .order_by('-cantidad_vendida')
    
    def cantidad_total_por_productos(
        self, 
        year: int =tz.now().year,
        month: int =tz.now().month,
    ):
        """
        procesa la informacion en un formato facilmente
        usable para el componente 'progress'
        """
        from .models import Producto
        queryset = self.queryset_cantidad_total_por_productos(year=year, month=month)
        cantidad_maxima = queryset[0]["cantidad_vendida"] + 1

        

        productos = []
        productos_no_vendidos = list(Producto.objects.values_list('nombre', flat=True))

        for item in queryset:
            title = item["producto__nombre"]
            value = (item["cantidad_vendida"] / cantidad_maxima) * 100 

            productos.append({
                "title":title,
                "value":value,
                "description": f"{value} Unidades"
            })

            try:
                index = productos_no_vendidos.index(title)
                productos_no_vendidos.pop(index)
            except:
                pass

        for item in productos_no_vendidos:
            productos.append({
                "title":item,
                "value":0,
                "description":'0 Unidades'
            })
        
        # items = sorted(productos, key=lambda x: x['value'], reverse=True)
        return productos
        # return {
        #     "productos": productos,
        #     # "maximo": cantidad_maxima
        # }

class ProduccionDetalleQueryset(models.QuerySet):
    def queryset_productos_producidos_al_mes(
        self, 
        year: int =tz.now().year,
        month: int =tz.now().month,
    ):
        """
        devuelve los totales producidos para cada producto
        para un mes y año 
        """
        return self.filter(
            produccion__ralada__fecha_ralada__year=year,
            produccion__ralada__fecha_ralada__month=month,
            producto__es_fabricado=True
        ).values(
            'producto__nombre',
            'producto__precio'
        ).annotate(total_producido=models.Sum('cantidad')).order_by('producto__nombre')
    
    def productos_producidos_al_mes(
        self, 
        year: int =tz.now().year,
        month: int =tz.now().month,
    ):
        from .models import Producto
        queryset = self.queryset_productos_producidos_al_mes(year=year, month=month)
        productos = []
        productos_no_producidos = list(Producto.objects.values_list('nombre', flat=True))
        
        for item in queryset:
            nombre = item["producto__nombre"]
            precio = item["producto__precio"]
            total = item["total_producido"]
            
            productos.append({
                "nombre":nombre,
                "precio":precio,
                "total":total
            })

            try:
                index = productos_no_producidos.index(nombre)
                productos_no_producidos.pop(index)
            except:
                pass

        for item in productos_no_producidos:
            productos.append({
                "nombre":item,
                "precio":0,
                "total":0
            })
        
        return sorted(productos, key=lambda x: x['nombre'])
    
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
   
    def bastones_procesados_al_mes(
        self, 
        year=tz.now().year,
        month=tz.now().month,
        variedad="luzeia",
    ):
        """
        lista con cantidad de bastones procesados mensuales
        para un mes, año y variedad  
        """
        return self.filtrar_por_fecha_y_tipo(year=year, month=month, variedad=variedad)\
            .aggregate(total_bastones=models.Sum('cantidad_bastones'))

    #MEJORAR
    def peso_procesado_al_mes(
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
            .aggregate(total_peso=Cast(models.Sum('peso_inicial'), models.FloatField()) / 1000)
            
            # .values('fecha_ralada')\
            # .annotate(kg_procesados=Cast(models.Sum('peso_inicial'), models.FloatField()) / 1000)\
            # .order_by('fecha_ralada')
