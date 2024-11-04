import calendar
import datetime
from typing import Collection, Iterable
from django.db import models
from django.utils import timezone as tz
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from .querysets import (
    VentaQueryset,
    RaladaQueryset,
    VentaItemQueryset,
    ProductoQueryset,
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


class CompraVidros(models.Model):
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=1)
    cantidad = models.PositiveIntegerField()
    fecha_registro = models.DateTimeField(auto_now=True)
    fecha_compra = models.DateField(default=tz.now)
    nota = models.TextField(blank=True, null=True)

    venta = models.OneToOneField(
        "Venta",
        related_name="compra_vidros",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __init__(self, *args, **kwargs):
        super(CompraVidros, self).__init__(*args, **kwargs)
        self._precio = 1

    @property
    def monto(self) -> models.DecimalField:
        return self.precio * self.cantidad


class UsoMetodoPago(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.ForeignKey(
        MetodoPago, related_name="usos_metodo_pago", on_delete=models.CASCADE
    )
    venta = models.ForeignKey(
        "Venta", related_name="usos_metodo_pago", on_delete=models.CASCADE
    )
    declarado = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Metodo {self.metodo} {self.venta}"

    @property
    def es_declarado(self):
        return "true" if self.declarado else "false"


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    es_fabricado = models.BooleanField(default=False)
    peso = models.PositiveIntegerField(default=0)
    tipo_guarana = models.ForeignKey(
        TipoGuarana,
        related_name="productos",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    objects = ProductoQueryset.as_manager()

    def __str__(self) -> str:
        return self.nombre

    class Meta:
        verbose_name = "ModelName"
        verbose_name_plural = "ModelNames"
        ordering = ["precio", "tipo_guarana", "-peso", "nombre"]
        indexes = [models.Index(fields=["precio", "tipo_guarana", "-peso", "nombre"])]


class Venta(models.Model):
    nota = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateField(default=tz.now)
    fecha_registro = models.DateTimeField(auto_now=True)
    # compra_vidros = models.ForeignKey(CompraVidros, related_name="venta", on_delete=models.SET_NULL, blank=True, null=True)

    objects = VentaQueryset.as_manager()

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

    # def clean(self):
    #     super().clean()
    #     if not self.usos_metodo_pago.exists():
    #         raise ValidationError("A venda debe ter pelo menos um método de pago asociado.")

    @property
    def fecha_corta(self) -> str:
        return self.fecha_venta.strftime("%d/%m/%Y")

    def __str__(self) -> str:
        return f"{self.fecha_corta} R$ {self.total}"

    @property
    def title(self):
        return mark_safe(f"Venda por R&#36; {self.total}")

    @property
    def total_bruto(self) -> models.DecimalField:
        total = 0
        for item in self.items.all():
            total += item.precio * item.cantidad
        return total


class VentaItem(models.Model):
    venta = models.ForeignKey(Venta, related_name="items", on_delete=models.CASCADE)
    producto = models.ForeignKey(
        Producto, related_name="venta_items", on_delete=models.CASCADE
    )
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    fecha_registro = models.DateTimeField(auto_now=True)
    objects = VentaItemQueryset.as_manager()

    def __str__(self) -> str:
        return f"{self.cantidad} x {self.producto}"

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
    tipo_guarana = models.ForeignKey(
        TipoGuarana, related_name="sacos", on_delete=models.PROTECT
    )
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    fecha_registro = models.DateTimeField(auto_now=True)
    fecha_llega = models.DateField(default=tz.now)

    @property
    def nombre_largo(self) -> str:
        return f"Saco {self.numero} - {self.tipo_guarana.nombre} - {self.peso} kg"

    def __str__(self):
        return f"{self.tipo_guarana.nombre.capitalize()} - Saco {self.numero}"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Produccion(models.Model):
    consumo = models.PositiveIntegerField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now=True)
    nota = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Produccion de {self.ralada}"

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def full_clean(self, *args, **kwargs) -> None:
        return super().full_clean(*args, **kwargs)

    class Meta:
        verbose_name = "Produccion"
        verbose_name_plural = "- Producciones"

    def __init__(self, *args, **kwargs):
        super(Produccion, self).__init__(*args, **kwargs)
        self._peso_maximo = None
        self._tipo_guarana = None

    @property
    def peso_maximo(self) -> int | None:
        return self._peso_maximo

    @property
    def tipo_guarana(self) -> TipoGuarana | None:
        return self._tipo_guarana

    @peso_maximo.setter
    def peso_maximo(self, n: int):
        self._peso_maximo = n

    @tipo_guarana.setter
    def tipo_guarana(self, tipo_guarana: TipoGuarana):
        self._tipo_guarana = tipo_guarana


class Periodo(models.Model):
    nombre = models.CharField(max_length=100)
    inicio = models.DateField()
    final = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=False)

    @property
    def inicio_fecha_formato(self):
        return self.inicio.strftime("%Y-%m-%d")
         
    def __str__(self):
        if not self.final:
            return f"{self.nombre} iniciado em {self.inicio}"
        return f"{self.nombre} do {self.inicio} ate {self.final} "
    
    def fecha_utlimo_dia_del_mes(self, fecha:datetime.date):
        ultimo_dia = calendar.monthrange(fecha.year, fecha.month)[1]
        ultimo_dia_del_mes = datetime.date(fecha.year, fecha.month, ultimo_dia)

    def rango_fechas(self) -> tuple[datetime.date, datetime.date]:
        # the period is well define
        if self.final:
            return (self.inicio, self.final)
        
        # the period is open
        elif self.activo:
            final = self.fecha_utlimo_dia_del_mes(tz.now())
            return (self.inicio, final)
    
        # the period was close but the end is lost
        # This will work as long as the periods are one month long and the current period has ended no less than a week before the end of the month.
        else:
            fecha = self.inicio + datetime.timedelta(days=7)
            final = self.fecha_utlimo_dia_del_mes(fecha)
            return (self.inicio, final)

        
    # class Meta:
    #     ordering = ["pk"]
    #     indexes = [
    #         models.Index(fields=["pk"])
    #     ]


class Ralada(models.Model):
    """
    lote de procesamiento de los bastones de guarana
    expresado en gm
    """

    produccion = models.OneToOneField(
        Produccion, related_name="ralada", on_delete=models.CASCADE
    )

    numero = models.PositiveIntegerField(blank=True, null=True)
    cantidad_bastones = models.PositiveIntegerField(blank=True, null=True)
    saco = models.ForeignKey(Saco, related_name="ralada", on_delete=models.PROTECT)
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
        return f"Ralada do {self.saco.tipo_guarana} Nº {self.numero} do Saco Nº {self.saco.numero}"


class ProduccionDetalle(models.Model):
    produccion = models.ForeignKey(
        Produccion, related_name="detalles", on_delete=models.CASCADE
    )
    producto = models.ForeignKey(
        Producto, related_name="producciones", on_delete=models.CASCADE
    )
    cantidad = models.PositiveIntegerField()

    fecha_registro = models.DateTimeField(auto_now=True)

    @property
    def peso_producido(self):
        return self.cantidad * self.producto.peso

    def __str__(self) -> str:
        return f"{self.cantidad} x {self.producto}"


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
    anotaciones = models.ForeignKey(
        "AnotacionInventario",
        related_name="cierre_inventarios",
        on_delete=models.CASCADE,
    )
    fecha_registro = models.DateTimeField(auto_now=True)
    fecha_inventario = models.DateField(default=tz.now)


class AnotacionInventario(models.Model):
    productos = models.ForeignKey(
        Producto, related_name="anotaciones_inventario", on_delete=models.CASCADE
    )
    cantidad = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
