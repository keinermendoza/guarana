
from django.db import models
from django.utils import timezone as tz
class TipoGuarana(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.nombre
    
    class Meta:
        verbose_name = "Variedad de Guarana"
        verbose_name_plural = "Variedades de Guarana"
    
class MetodoPago(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self) -> str:
        return self.nombre
    
    class Meta:
        verbose_name = "Metodo de Pago"
        verbose_name_plural = "Metodos de Pago"

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self) -> str:
        return self.nombre
    
class Venta(models.Model):
    metodo_pago = models.ManyToManyField(MetodoPago, related_name="ventas")
    nota = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_venta = models.DateTimeField(default=tz.now)
    fecha_registro = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "- Ventas"

class VentaItem(models.Model):
    venta = models.ForeignKey(Venta, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, related_name='detalles', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
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
    fecha_llega = models.DateTimeField(default=tz.now)


    @property
    def nombre_largo(self) -> str:
        return f'Saco {self.numero} - {self.tipo_guarana.nombre} - {self.peso} kg'

    def __str__(self):
        return f'Saco {self.numero}'
    
   
        
class Produccion(models.Model):
    # ralada = models.OneToOneField(Ralada, related_name="produccion", on_delete=models.CASCADE)
    consumo = models.PositiveIntegerField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now=True)
    nota = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Produccion de {self.ralada}'
    
    class Meta:
        verbose_name = "Produccion"
        verbose_name_plural = "- Producciones"

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
    fecha_ralada = models.DateTimeField(default=tz.now)

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
