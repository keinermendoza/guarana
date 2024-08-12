from collections import defaultdict
from decimal import Decimal
from typing import Iterable
from django.db import models
from django.utils import timezone as tz
from django.db.models import Sum, FloatField, DecimalField
from django.db.models.functions import TruncDay, Cast

class TipoGuarana(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.nombre
    
    class Meta:
        verbose_name = "Variedad de Guarana"
        verbose_name_plural = "Variedades de Guarana"
    
class MetodoPago(models.Model):
    class Tipo(models.TextChoices):
        CARTON = ("C", "Cartão")
        EFECTIVO = ("D", "Dinheiro")
        PIX = ("P", "Pix")

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=1, choices=Tipo.choices, default=Tipo.CARTON)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self) -> str:
        return self.nombre
    
    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Metodo de Pago"
        verbose_name_plural = "Metodos de Pago"

class UsoMetodoPago(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    metodo = models.ForeignKey(MetodoPago, related_name="usos_metodo_pago", on_delete=models.CASCADE)
    venta = models.ForeignKey("Venta", related_name="usos_metodo_pago", on_delete=models.CASCADE)
    declarado = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Metodo {self.metodo} {self.venta}"

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    
    def __str__(self) -> str:
        return self.nombre

class VentaQueryset(models.QuerySet):
    def data_for_chartjs(
        self,
        year: int = tz.now().year,
        month: int = tz.now().month,
    ) -> dict:
        """
        formatea data para usar grafico de barras (mensual) en chartjs
        """
        # pix = []
        # efectivo = []
        # carton = []
        # fechas = set()

        # check_fechas = set()

        # resultados_dia_metodo = self.venta_mensual_por_dia_y_metodo_pago(year=year, month=month)
        # for data in resultados_dia_metodo:
        #     pix.append(self.total_diario_por_metodo(data=data, fechas=check_fechas, tipo=MetodoPago.Tipo.PIX))
        #     efectivo.append(self.total_diario_por_metodo(data=data, fechas=check_fechas, tipo=MetodoPago.Tipo.EFECTIVO))
        #     carton.append(self.total_diario_por_metodo(data=data, fechas=check_fechas, tipo=MetodoPago.Tipo.CARTON))
        #     fechas.add(data['fecha_venta'].strftime('%d/%m'))
            
        #     check_fechas.add(data['fecha_venta'])
        
        # return {
        #     "fechas":fechas,
        #     "efectivo":efectivo,
        #     "pix":pix,
        #     "carton":carton
        # }
     # Inicializar el diccionario con listas vacías
        
        fechas = []
        efectivo = []
        pix = []
        carton = []

        # Crear un set para rastrear las fechas únicas
        fechas_set = set()

        # Inicializar un diccionario para almacenar las ventas por fecha y método de pago
        ventas_por_metodo = defaultdict(lambda: {'D': 0, 'P': 0, 'C': 0})
       
        ventas = self.venta_mensual_por_dia_y_metodo_pago(year=year, month=month)

        # Recorrer las ventas y llenar el diccionario
        for venta in ventas:
            fecha = venta['fecha_venta']
            metodo_pago = venta['metodo_pago__tipo']
            total_ventas = venta['total_ventas']

            # Añadir la fecha al set de fechas
            fechas_set.add(fecha)

            # Sumar las ventas según el método de pago
            ventas_por_metodo[fecha][metodo_pago] += total_ventas

        # Ordenar las fechas
        fechas_ordenadas = sorted(fechas_set)

        # Llenar las listas para efectivo, pix y carton
        for fecha in fechas_ordenadas:
            fechas.append(fecha.strftime('%d/%m'))
            efectivo.append(ventas_por_metodo[fecha]['D'])
            pix.append(ventas_por_metodo[fecha]['P'])
            carton.append(ventas_por_metodo[fecha]['C'])

        # Crear el diccionario final
        resultado = {
            "fechas": fechas,
            "efectivo": efectivo,
            "pix": pix,
            "carton": carton
        }

        return resultado

    # def total_mensual_por_metodo_pago(
    #     self,
    #     year: int = tz.now().year,
    #     month: int = tz.now().month
    # ) -> list[dict[str, float]]:
    #     total_metodo_pago = defaultdict(Decimal)

    #     queryset_totales_por_dia = self.venta_mensual_por_dia_y_metodo_pago(year=year, month=month)
    #     for dia in queryset_totales_por_dia:
    #         pass


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
             .annotate(total_ventas=Sum('total', output_field=DecimalField()))\
             .order_by('fecha_venta', 'metodo_pago__tipo')
    
    

    def total_diario_por_metodo(
        self,
        data: dict,
        tipo: str,
        fechas
    )-> list[int, int]:
        """
        regresa una lista representando una barra
        en grafico para chartjs
        """
        if tipo == data['metodo_pago__tipo']:
            return [0, float(data['total_ventas'])]
        else:
            if data['fecha_venta'] not in fechas:
                print(data['fecha_venta'], fechas)
                return [0,0]
            return None

class Venta(models.Model):
    metodo_pago = models.ManyToManyField(MetodoPago, related_name="ventas")
    nota = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateField(default=tz.now)
    fecha_registro = models.DateTimeField(auto_now=True)
    compra_vidros = models.ForeignKey("CompraVidros", related_name="venta", on_delete=models.SET_NULL, blank=True, null=True)

    objects = VentaQueryset.as_manager()
    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

    @property
    def fecha_venta_corta(self) -> str:
        return self.fecha_venta.strftime("%d/%m/%Y")
    
    def __str__(self) -> str:
        return f"R$ {self.total} dia {self.fecha_venta_corta}"

class VentaItem(models.Model):
    venta = models.ForeignKey(Venta, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, related_name='detalles', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    fecha_registro = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.cantidad} x {self.producto}'
    
    class Meta:
        verbose_name = "Item Vendido"
        verbose_name_plural = "Items Vendidos"
    
class Saco(models.Model):
    """
    expresado en kg
    """
    numero = models.PositiveIntegerField()
    tipo_guarana = models.ForeignKey(TipoGuarana, related_name="sacos", on_delete=models.PROTECT)
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    fecha_registro = models.DateTimeField(auto_now=True)
    fecha_llega = models.DateField(default=tz.now)


    @property
    def nombre_largo(self) -> str:
        return f'Saco {self.numero} - {self.tipo_guarana.nombre} - {self.peso} kg'

    def __str__(self):
        return f'Saco {self.numero}'
    
   
        
class Produccion(models.Model):
    consumo = models.PositiveIntegerField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now=True)
    nota = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Produccion de {self.ralada}'
    
    class Meta:
        verbose_name = "Produccion"
        verbose_name_plural = "- Producciones"

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
            .annotate(total_bastones=Sum('cantidad_bastones'))\
            .order_by('fecha_ralada')
        
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
            .annotate(kg_procesados=Cast(Sum('peso_inicial'), FloatField()) / 1000)\
            .order_by('fecha_ralada')


class Ralada(models.Model):
    """
    lote de procesamiento de los bastones de guarana
    expresado en gm
    """
    produccion = models.OneToOneField(Produccion, related_name="ralada", on_delete=models.CASCADE)

    numero = models.PositiveIntegerField(blank=True, null=True)
    cantidad_bastones = models.PositiveIntegerField(blank=True, null=True)
    saco = models.ForeignKey(Saco, related_name="ralada", on_delete=models.SET_NULL, blank=True, null=True)
    peso_inicial = models.PositiveIntegerField(blank=True, null=True)
    sobra_inicial = models.PositiveIntegerField(blank=True, null=True)
    sobra_final = models.PositiveIntegerField(blank=True, null=True)
    peso_final = models.PositiveIntegerField(blank=True, null=True)

    fecha_registro = models.DateTimeField(auto_now=True)
    fecha_ralada = models.DateField(default=tz.now)
    objects = RaladaQueryset.as_manager()

    @property
    def peso_peneirado(self) -> int:
        """expresado en gm"""
        return self.peso_final - self.sobra_final
    
    @property
    def perdida(self) -> int:
        """expresado en gm"""
        return self.sobra_final - self.sobra_final
    
    def __str__(self):
        return f'Ralada {self.numero} - {self.saco}'

class ProduccionDetalle(models.Model):
    produccion = models.ForeignKey(Produccion, related_name="detalles", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, related_name="producciones", on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha_registro = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return f'{self.cantidad} x {self.producto}'

class CompraVidros(models.Model):
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    cantidad = models.PositiveIntegerField()
    fecha_registro = models.DateTimeField(auto_now=True)
    fecha_compra = models.DateField(default=tz.now)
    nota = models.TextField(blank=True, null=True)


class Gasto(models.Model):
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    fecha_registro = models.DateTimeField(auto_now=True)
    fecha_gasto = models.DateField(default=tz.now)
    nota = models.TextField(blank=True, null=True)


class Consumo(models.Model):
    productos = models.ManyToManyField(Producto, related_name="consumo")
    cantidad = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    fecha_registro = models.DateTimeField(auto_now=True)
    fecha_consumo = models.DateField(default=tz.now)
    nota = models.TextField(blank=True, null=True)

class Inventario(models.Model):
    anotaciones = models.ForeignKey("AnotacionInventario", related_name="cierre_inventarios", on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now=True)
    fecha_inventario = models.DateField(default=tz.now)

class AnotacionInventario(models.Model):
    productos = models.ForeignKey(Producto, related_name="anotaciones_inventario", on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    