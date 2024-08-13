from django.utils import timezone as tz
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from decimal import Decimal
import datetime
from core.models import (
    Venta,
    MetodoPago,
    Ralada,
    Produccion,
    Saco,
    TipoGuarana
)

class VentaModelCreation(TestCase):
    def test_total_field_is_required(self):
        with self.assertRaises(IntegrityError):
            Venta.objects.create()

    def test_total_is_the_only_required_field(self):
        venta = Venta.objects.create(total=120)
        self.assertIsInstance(venta, Venta)

class MetodoPagoCreation(TestCase):
    def test_nombre_field_is_required(self):
        with self.assertRaises(ValidationError):
            MetodoPago.objects.create()
    
    def test_nombre_is_the_only_required_field(self):
        metodo = MetodoPago.objects.create(nombre="Visa Credito")
        self.assertIsInstance(metodo, MetodoPago)
        self.assertEquals(metodo.tipo, MetodoPago.Tipo.CARTON)


class VentaQuerysetMethods(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        MetodoPago.objects.create(nombre="Visa Credito")
        MetodoPago.objects.create(nombre="Visa Debito")
        MetodoPago.objects.create(nombre="Mastercard Credito")
        MetodoPago.objects.create(nombre="Mastercard Debito")
        MetodoPago.objects.create(nombre="Pix", tipo=MetodoPago.Tipo.PIX)
        MetodoPago.objects.create(nombre="Dinheiro", tipo=MetodoPago.Tipo.EFECTIVO)

    def setUp(self):
        Venta.objects.create(nota='1', total=50, fecha_venta='2024-08-11')
        Venta.objects.create(nota='2', total=110, fecha_venta='2024-08-11')
        Venta.objects.create(nota='3', total=50, fecha_venta='2024-08-11')
        Venta.objects.create(nota='4', total=90, fecha_venta='2024-08-11')

        Venta.objects.create(nota='5', total=125, fecha_venta='2024-08-12')
        Venta.objects.create(nota='6', total=175, fecha_venta='2024-08-12')
        Venta.objects.create(nota='7', total=100, fecha_venta='2024-08-12')

        Venta.objects.create(nota='8', total=75, fecha_venta='2024-08-13')
        Venta.objects.create(nota='9', total=25, fecha_venta='2024-08-13')
        Venta.objects.create(nota='10', total=50, fecha_venta='2024-08-13')
        Venta.objects.create(nota='11', total=150, fecha_venta='2024-08-13')
        Venta.objects.create(nota='12', total=75, fecha_venta='2024-08-13')
        Venta.objects.create(nota='13', total=25, fecha_venta='2024-08-13')
        Venta.objects.create(nota='14', total=200, fecha_venta='2024-08-13')

    def test_unico_metodo_pago_queryset__venta_mensual_por_dia_y_metodo_pago(self):
        """
        agrupa las ventas en tres objetos sumando todas las ventas por dia
        """
        pix = MetodoPago.objects.get(nombre="Pix")
        #
        for venta in Venta.objects.all():
            venta.metodo_pago.add(pix)

        resultado = Venta.objects.venta_mensual_por_dia_y_metodo_pago(year=2024, month=8)

        self.assertEquals(len(resultado), 3)
        dia_11, dia_12, dia_13 = resultado 

        self.assertEquals(MetodoPago.Tipo.PIX, dia_11['metodo_pago__tipo'])
        self.assertEquals(dia_11['metodo_pago__tipo'], dia_12['metodo_pago__tipo'])
        self.assertEquals(dia_12['metodo_pago__tipo'], dia_13['metodo_pago__tipo'])

        self.assertEquals(dia_11['fecha_venta'], datetime.date(2024, 8, 11))
        self.assertEquals(dia_12['fecha_venta'], datetime.date(2024, 8, 12))
        self.assertEquals(dia_13['fecha_venta'], datetime.date(2024, 8, 13))

        self.assertEquals(dia_11['total_ventas'], Decimal('300.00'))
        self.assertEquals(dia_12['total_ventas'], Decimal('400.00'))
        self.assertEquals(dia_13['total_ventas'], Decimal('600.00'))


    def test_dos_metodo_pago_queryset__venta_mensual_por_dia_y_metodo_pago(self):
        """
        agrupa las ventas en 6 objetos sumando todas las ventas por dia y metodo de pago
        """
        pix = MetodoPago.objects.get(nombre="Pix")
        efectivo = MetodoPago.objects.get(nombre="Dinheiro")

        for i, venta in enumerate(Venta.objects.all(), 1):
            if i % 2 == 1:
                venta.metodo_pago.add(pix)
            else:
                venta.metodo_pago.add(efectivo)
            
        result = Venta.objects.venta_mensual_por_dia_y_metodo_pago(year=2024, month=8)
        self.assertEquals(len(result), 6)
        dia_11_efectivo, dia_11_pix, dia_12_efectivo, dia_12_pix, dia_13_efectivo, dia_13_pix = result

        self.assertEquals(MetodoPago.Tipo.EFECTIVO, dia_11_efectivo['metodo_pago__tipo'])
        self.assertEquals(MetodoPago.Tipo.PIX, dia_11_pix['metodo_pago__tipo'])
        self.assertEquals(MetodoPago.Tipo.EFECTIVO, dia_12_efectivo['metodo_pago__tipo'])
        self.assertEquals(MetodoPago.Tipo.PIX, dia_12_pix['metodo_pago__tipo'])
        self.assertEquals(MetodoPago.Tipo.EFECTIVO, dia_13_efectivo['metodo_pago__tipo'])
        self.assertEquals(MetodoPago.Tipo.PIX, dia_13_pix['metodo_pago__tipo'])


        self.assertEquals(dia_11_pix['fecha_venta'], datetime.date(2024, 8, 11))
        self.assertEquals(dia_12_pix['fecha_venta'], datetime.date(2024, 8, 12))
        self.assertEquals(dia_13_pix['fecha_venta'], datetime.date(2024, 8, 13))

        self.assertEquals(dia_11_efectivo['total_ventas'], Decimal('200.00'))
        self.assertEquals(dia_12_efectivo['total_ventas'], Decimal('175.00'))
        self.assertEquals(dia_13_efectivo['total_ventas'], Decimal('400.00'))

    def test_venta_diaria(self):
        """
        regresa listas representando el total de la venta diaria
        una lista por cada metodo de pago, un item por cada día
        """
        pix = MetodoPago.objects.get(nombre="Pix")
        efectivo = MetodoPago.objects.get(nombre="Dinheiro")

        for i, venta in enumerate(Venta.objects.all(), 1):
            if i % 2 == 1:
                venta.metodo_pago.add(pix)
            else:
                venta.metodo_pago.add(efectivo)

        resultados = Venta.objects.venta_diaria(year=2024, month=8)
        
        self.assertIn('11/08', resultados['fechas'])
        self.assertIn('12/08', resultados['fechas'])
        self.assertIn('13/08', resultados['fechas'])

        self.assertEquals(len(resultados['efectivo']), 3)
        self.assertEquals(sum(resultados['efectivo']), 775)

        self.assertEquals(len(resultados['pix']), 3)
        self.assertEquals(sum(resultados['pix']), 525)

        self.assertEquals(len(resultados['carton']), 3)
        self.assertEquals(sum(resultados['carton']), 0)


    def test_totales_mensuales(self):
        """
        """
        pix = MetodoPago.objects.get(nombre="Pix")
        efectivo = MetodoPago.objects.get(nombre="Dinheiro")

        for i, venta in enumerate(Venta.objects.all(), 1):
            if i % 2 == 1:
                venta.metodo_pago.add(pix)
            else:
                venta.metodo_pago.add(efectivo)

        resultados = Venta.objects.totales_mensuales(year=2024, month=8)

        self.assertEquals(len(resultados), 3)
        self.assertEquals(resultados['efectivo'], 775)
        self.assertEquals(resultados['pix'], 525)
        self.assertEquals(resultados['carton'], 0)

    def test_data_grafico_bar_chartjs(self):
        """
        """
        pix = MetodoPago.objects.get(nombre="Pix")
        efectivo = MetodoPago.objects.get(nombre="Dinheiro")

        for i, venta in enumerate(Venta.objects.all(), 1):
            if i % 2 == 1:
                venta.metodo_pago.add(pix)
            else:
                venta.metodo_pago.add(efectivo)

        resultados = Venta.objects.data_grafico_bar_chartjs(year=2024, month=8)

        self.assertEquals(len(resultados), 4)
        self.assertEquals(len(resultados['efectivo']), 3)
        self.assertEquals(len(resultados['pix']), 3)
        self.assertEquals(len(resultados['carton']), 3)

        self.assertEquals(resultados['carton'], [[0,0],[0,0],[0,0]])
        self.assertEquals(resultados['efectivo'], [[0,200],[0,175],[0,400]])


class RaladaSacoModelCreation(TestCase):
    def test_ralada_required_fields(self):
        produccion = Produccion.objects.create()
        ralada = Ralada.objects.create(produccion=produccion)
        self.assertIsInstance(ralada, Ralada)

    def test_tipo_guarana_required_fields(self):
        tipo = TipoGuarana.objects.create(nombre="Maue do Indio")
        self.assertIsInstance(tipo, TipoGuarana)

    def test_saco_test_required_fields(self):
        tipo = TipoGuarana.objects.create(nombre="Tibiriça")
        saco = Saco.objects.create(numero=312, tipo_guarana=tipo)
        self.assertIsInstance(saco, Saco)


class RaladaQuerysetMethods(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        maue = TipoGuarana.objects.create(nombre="Maue")
        luzeia = TipoGuarana.objects.create(nombre="Luzeia")
        Saco.objects.create(numero=301, tipo_guarana=maue)
        Saco.objects.create(numero=303, tipo_guarana=luzeia)

    def setUp(self):
        saco_301 = Saco.objects.get(numero=301)
        saco_303 = Saco.objects.get(numero=303)

        p1 = Produccion.objects.create()
        p2 = Produccion.objects.create()
        p3 = Produccion.objects.create()
        p4 = Produccion.objects.create()
        p5 = Produccion.objects.create()
        p6 = Produccion.objects.create()
        
        p7 = Produccion.objects.create()


        Ralada.objects.create(produccion=p1, saco=saco_301, cantidad_bastones=25, peso_inicial=5100, peso_final=4950 ,fecha_ralada='2024-07-11')
        Ralada.objects.create(produccion=p2, saco=saco_303, cantidad_bastones=30, peso_inicial=5300, peso_final=5200 ,fecha_ralada='2024-07-15')
        Ralada.objects.create(produccion=p3, saco=saco_301, cantidad_bastones=25, peso_inicial=4900, peso_final=4750 ,fecha_ralada='2024-07-19')
        Ralada.objects.create(produccion=p4, saco=saco_303, cantidad_bastones=30, peso_inicial=5125, peso_final=4990 ,fecha_ralada='2024-07-24')
        Ralada.objects.create(produccion=p5, saco=saco_301, cantidad_bastones=25, peso_inicial=5050, peso_final=4700 ,fecha_ralada='2024-07-29')
        Ralada.objects.create(produccion=p6, saco=saco_303, cantidad_bastones=30, peso_inicial=5400, peso_final=5250 ,fecha_ralada='2024-07-30')
        
        Ralada.objects.create(produccion=p7, saco=saco_303, cantidad_bastones=30, peso_inicial=5400, peso_final=5250 ,fecha_ralada='2024-08-05')

    def test_filtrar_por_fecha_y_tipo(self):
        """
        filtra raladas por mes, año y variedad de guarana (usando el nombre en del tipo de guarana en iexac)
        """
        resultado = Ralada.objects.filtrar_por_fecha_y_tipo(year=2024, month=7, variedad="maue")
        self.assertEquals(len(resultado), 3)

        resultado = Ralada.objects.filtrar_por_fecha_y_tipo(year=2024, month=7, variedad="luzeia")
        self.assertEquals(len(resultado), 3)

        resultado = Ralada.objects.filtrar_por_fecha_y_tipo(year=2024, month=8, variedad="maue")
        self.assertEquals(len(resultado), 0)

        resultado = Ralada.objects.filtrar_por_fecha_y_tipo(year=2024, month=8, variedad="luzeia")
        self.assertEquals(len(resultado), 1)

    # NO TIENE MUCHO SENTIDO
    # def test_bastones_diarios(self):
    #     resultado = Ralada.objects.bastones_diarios(year=2024, month=7, variedad="maue")
    #     print(resultado)
    #     self.assertEquals(1,1)

    # NO TIENE MUCHO SENTIDO
    # def test_procesado_diario(self):
    #     resultado = Ralada.objects.procesado_diario(year=2024, month=7, variedad="maue")
    #     print(resultado)
    #     self.assertEquals(1,1)