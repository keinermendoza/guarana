import random
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
    TipoGuarana,
    Producto,
    ProduccionDetalle,
    VentaItem
)

class MinimumRequieredFieldsPerClass(TestCase):
    def test_venta_required_field(self):
        venta = Venta.objects.create(total=120)
        self.assertIsInstance(venta, Venta)
    
    def test_metodo_pago_required_field(self):
        metodo = MetodoPago.objects.create(nombre="Visa Credito")
        self.assertIsInstance(metodo, MetodoPago)
        self.assertEquals(metodo.tipo, MetodoPago.Tipo.CARTON)

    def test_ralada_required_fields(self):
        produccion = Produccion.objects.create()
        ralada = Ralada.objects.create(produccion=produccion)
        self.assertIsInstance(ralada, Ralada)

    def test_saco_test_required_fields(self):
        tipo = TipoGuarana.objects.create(nombre="Tibiriça")
        saco = Saco.objects.create(numero=312, tipo_guarana=tipo)
        self.assertIsInstance(saco, Saco)

    def test_tipo_guarana_required_fields(self):
        tipo = TipoGuarana.objects.create(nombre="Maue do Indio")
        self.assertIsInstance(tipo, TipoGuarana)

    def test_producto_required_fields(self):
        producto = Producto.objects.create(nombre="Luzeia 70g", precio=33)
        self.assertIsInstance(producto, Producto)
    
    def test_produccion_detalle_required_fields(self):
        produccion = Produccion.objects.create()
        producto = Producto.objects.create(nombre="luzeia 70g", precio=33)
        produccion_detalle = ProduccionDetalle.objects.create(produccion=produccion, producto=producto, cantidad=10)
        self.assertIsInstance(produccion_detalle, ProduccionDetalle)
    
    def test_venta_item_required_fields(self):
        venta = Venta.objects.create(total=66)
        producto = Producto.objects.create(nombre="luzeia 70g", precio=33)
        venta_item = VentaItem.objects.create(producto=producto, precio=producto.precio, cantidad=2, venta=venta)
        self.assertIsInstance(venta_item, VentaItem)

   


class VentaQuerysetMethods(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Producto.objects.create(nombre="luzeia 70gm", precio=20, es_fabricado=True)
        Producto.objects.create(nombre="luzeia 120gm", precio=50, es_fabricado=True)

        Producto.objects.create(nombre="maue 70gm", precio=25, es_fabricado=True)
        Producto.objects.create(nombre="maue 120gm", precio=60, es_fabricado=True)
        Producto.objects.create(nombre="maue 200gm", precio=100, es_fabricado=True)


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

        Venta.objects.create(nota='out range of time', total=200, fecha_venta='2024-07-13')
        Venta.objects.create(nota='out range of time', total=200, fecha_venta='2024-09-13')
        Venta.objects.create(nota='out range of time', total=200, fecha_venta='2024-06-13')


        


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


    def test_venta_item_cantidad_total_por_productos(self):
        luz_70 = Producto.objects.get(nombre="luzeia 70gm")
        luz_120 = Producto.objects.get(nombre="luzeia 120gm")
        maue_70 = Producto.objects.get(nombre="maue 70gm")
        maue_120 = Producto.objects.get(nombre="maue 120gm")
        maue_200 = Producto.objects.get(nombre="maue 200gm")


        for i, venta in enumerate(Venta.objects.all(), 1):
            if i % 2 == 1:
                VentaItem.objects.create(producto=luz_70, venta=venta, cantidad=1, precio=luz_70.precio)
            else:
                VentaItem.objects.create(producto=luz_120, venta=venta, cantidad=1, precio=luz_120.precio)
            

        cantidad_total_por_productos = VentaItem.objects.cantidad_total_por_productos(year=2024, month=8)
        print(cantidad_total_por_productos)

        self.assertEquals(Venta.objects.count(), VentaItem.objects.count())
        # self.assertEquals(len(cantidad_total_por_productos), 2)
        
        # # productos debe contener un diccionario para cada producto de fabricacion registrado sin importar que no haya sido vendido
        # self.assertEquals(len(cantidad_total_por_productos['productos']), 5)

        # # el maximo debe ser 1 numero mayor a la mayor cantidad de productos vendidos (en este caso 7)
        # self.assertEquals(cantidad_total_por_productos['maximo'], 8)

        # # todos los elementos del dict productos contienen las claves 'nombre' y 'total'
        # self.assertTrue("nombre" in cantidad_total_por_productos['productos'][random.randint(0,4)].keys())
        # self.assertTrue("total" in cantidad_total_por_productos['productos'][random.randint(0,4)].keys())


class RaladaQuerysetMethods(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        maue = TipoGuarana.objects.create(nombre="Maue")
        luzeia = TipoGuarana.objects.create(nombre="Luzeia")
        saco_301 = Saco.objects.create(numero=301, tipo_guarana=maue)
        saco_303 = Saco.objects.create(numero=303, tipo_guarana=luzeia)
        
        luz_70 = Producto.objects.create(nombre="luzeia 70gm", precio=33, es_fabricado=True)
        luz_90 = Producto.objects.create(nombre="luzeia 90gm", precio=42, es_fabricado=True)
        luz_120 = Producto.objects.create(nombre="luzeia 120gm", precio=55, es_fabricado=True)
        luz_200 = Producto.objects.create(nombre="luzeia 200gm", precio=88, es_fabricado=True)

        maue_70 = Producto.objects.create(nombre="maue 70gm", precio=39, es_fabricado=True)
        maue_90 = Producto.objects.create(nombre="maue 90gm", precio=50, es_fabricado=True)
        maue_120 = Producto.objects.create(nombre="maue 120gm", precio=66, es_fabricado=True)
        maue_200 = Producto.objects.create(nombre="maue 200gm", precio=106, es_fabricado=True)

        p1 = Produccion.objects.create(nota="1")
        p2 = Produccion.objects.create(nota="2")
        p3 = Produccion.objects.create(nota="3")
        p4 = Produccion.objects.create(nota="4")
        p5 = Produccion.objects.create(nota="5")
        p6 = Produccion.objects.create(nota="6")
        p7 = Produccion.objects.create(nota="7")

        ProduccionDetalle.objects.create(produccion=p1, producto=maue_200, cantidad=24)
        ProduccionDetalle.objects.create(produccion=p1, producto=maue_120, cantidad=1)
        ProduccionDetalle.objects.create(produccion=p1, producto=maue_70, cantidad=4)

        ProduccionDetalle.objects.create(produccion=p2, producto=luz_200, cantidad=25)
        ProduccionDetalle.objects.create(produccion=p2, producto=luz_120, cantidad=1)
        ProduccionDetalle.objects.create(produccion=p2, producto=luz_70, cantidad=1)

        ProduccionDetalle.objects.create(produccion=p3, producto=maue_200, cantidad=23)
        ProduccionDetalle.objects.create(produccion=p3, producto=maue_120, cantidad=1)
        ProduccionDetalle.objects.create(produccion=p3, producto=maue_70, cantidad=4)


        ProduccionDetalle.objects.create(produccion=p4, producto=luz_200, cantidad=24)
        ProduccionDetalle.objects.create(produccion=p4, producto=luz_120, cantidad=1)
        ProduccionDetalle.objects.create(produccion=p4, producto=luz_70, cantidad=10)


        ProduccionDetalle.objects.create(produccion=p5, producto=maue_200, cantidad=23)
        ProduccionDetalle.objects.create(produccion=p5, producto=maue_90, cantidad=1)

        ProduccionDetalle.objects.create(produccion=p6, producto=luz_200, cantidad=25)
        ProduccionDetalle.objects.create(produccion=p6, producto=luz_120, cantidad=2)


        Ralada.objects.create(produccion=p1, saco=saco_301, cantidad_bastones=25, peso_inicial=5100, peso_final=4950 ,fecha_ralada='2024-07-11')
        Ralada.objects.create(produccion=p2, saco=saco_303, cantidad_bastones=30, peso_inicial=5300, peso_final=5200 ,fecha_ralada='2024-07-15')
        Ralada.objects.create(produccion=p3, saco=saco_301, cantidad_bastones=25, peso_inicial=4900, peso_final=4750 ,fecha_ralada='2024-07-19')
        Ralada.objects.create(produccion=p4, saco=saco_303, cantidad_bastones=30, peso_inicial=5125, peso_final=4990 ,fecha_ralada='2024-07-24')
        Ralada.objects.create(produccion=p5, saco=saco_301, cantidad_bastones=25, peso_inicial=5050, peso_final=4700 ,fecha_ralada='2024-07-29')
        Ralada.objects.create(produccion=p6, saco=saco_303, cantidad_bastones=30, peso_inicial=5400, peso_final=5250 ,fecha_ralada='2024-07-30')
        
        Ralada.objects.create(produccion=p7, saco=saco_303, cantidad_bastones=30, peso_inicial=5400, peso_final=5250 ,fecha_ralada='2024-08-05')

        
    
    # def setUp(self):
        
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

    def test_bastones_procesados_al_mes(self):
        resultado_maue = Ralada.objects.bastones_procesados_al_mes(year=2024, month=7, variedad="maue")
        resultado_luzeia = Ralada.objects.bastones_procesados_al_mes(year=2024, month=7, variedad="luzeia")
        
        self.assertEquals(resultado_maue['total_bastones'], 75)
        self.assertEquals(resultado_luzeia['total_bastones'], 90)

    def test_peso_procesado_al_mes(self):
        resultado_maue = Ralada.objects.peso_procesado_al_mes(year=2024, month=7, variedad="maue")
        resultado_luzeia = Ralada.objects.peso_procesado_al_mes(year=2024, month=7, variedad="luzeia")
        
        self.assertEquals(resultado_maue['total_peso'],15.05)
        self.assertEquals(resultado_luzeia['total_peso'],15.825)


    # def test_productos_producidos_al_mes(self):
    #     resultado = ProduccionDetalle.objects.queryset_productos_producidos_al_mes(year=2024, month=7)
    #     for producto in resultado:
    #         print(producto)
      

    #     self.assertEquals(1,1)

    # def test_productos_producidos_al_mes(self):
    #     resultado = ProduccionDetalle.objects.productos_producidos_al_mes(year=2024, month=7)
    #     # for producto in resultado:
    #     #     print(producto)
    #     print(resultado)

    #     self.assertEquals(1,1)

