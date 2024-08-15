
from django.db import models
from django.utils import timezone as tz
from django.utils.safestring import mark_safe

from .querysets import (
    VentaQueryset,
    RaladaQueryset,
    VentaItemQueryset,
    ProductoQueryset
)

class TipoGuarana(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.nombre
    
    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)
    
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
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    metodo = models.ForeignKey(MetodoPago, related_name="usos_metodo_pago", on_delete=models.CASCADE)
    venta = models.ForeignKey("Venta", related_name="usos_metodo_pago", on_delete=models.CASCADE)
    declarado = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Metodo {self.metodo} {self.venta}"

    @property
    def es_declarado(self):
        return 'true' if self.declarado else 'false'
    
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    es_fabricado = models.BooleanField(default=False)

    objects = ProductoQueryset.as_manager()
    
    def __str__(self) -> str:
        return self.nombre

class Venta(models.Model):
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
    def fecha_corta(self) -> str:
        return self.fecha_venta.strftime("%d/%m/%Y")
    
    def __str__(self) -> str:
        return f"{self.fecha_corta} R$ {self.total}"
    
    @property
    def title(self):
        return mark_safe(f"Venda por R&#36; {self.total}")

class VentaItem(models.Model):
    venta = models.ForeignKey(Venta, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, related_name='venta_items', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    fecha_registro = models.DateTimeField(auto_now=True)
    objects = VentaItemQueryset.as_manager()
    
    def __str__(self) -> str:
        return f'{self.cantidad} x {self.producto}'
    
    @property
    def total(self):
        return float(self.precio * self.cantidad)
    
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
    
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

        
class Produccion(models.Model):
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
    