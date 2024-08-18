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
    UsoMetodoPago,
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
        tipo = TipoGuarana.objects.create(nombre="Maue do Indio")
        saco = Saco.objects.create(tipo_guarana=tipo, numero=288)

        ralada = Ralada.objects.create(produccion=produccion, saco=saco)
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

   
    def test_uso_metodo_pago_fields_required(self):
        metodo = MetodoPago.objects.create(nombre="Visa Credito")
        venta = Venta.objects.create(total=120)
        uso_metodo_pago = UsoMetodoPago.objects.create(metodo=metodo, venta=venta, monto=venta.total)
        self.assertIsInstance(uso_metodo_pago, UsoMetodoPago)

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




    def test_venta_queryset__kpi_totales_por_metodo(self):
        pix = MetodoPago.objects.get(nombre="Pix")
        efectivo = MetodoPago.objects.get(nombre="Dinheiro")

        for i, venta in enumerate(Venta.objects.all(), 1):
            if i % 2 == 1:
                UsoMetodoPago.objects.create(venta=venta, monto=venta.total, metodo=pix)
            else:
                UsoMetodoPago.objects.create(venta=venta, monto=venta.total, metodo=efectivo)

        resultados = Venta.objects.kpi_totales_por_metodo(year=2024, month=8)

        keys = {'title', 'metric', 'footer'}
        self.assertEquals(len(resultados), 2)
        self.assertTrue(keys.issubset(resultados[0].keys()))
        self.assertTrue(keys.issubset(resultados[1].keys()))
        self.assertEquals(resultados[0]['metric'], 'R$ 775.00')
        self.assertEquals(resultados[1]['metric'], 'R$ 525.00')



    def test_venta_queryset__grafico_bar_metodos_de_pago_diario(self):
        """
        """
        pix = MetodoPago.objects.get(nombre="Pix")
        efectivo = MetodoPago.objects.get(nombre="Dinheiro")

        for i, venta in enumerate(Venta.objects.all(), 1):
            if i % 2 == 1:
                UsoMetodoPago.objects.create(venta=venta, monto=venta.total, metodo=pix)
            else:
                UsoMetodoPago.objects.create(venta=venta, monto=venta.total, metodo=efectivo)

        resultados = Venta.objects.grafico_bar_metodos_de_pago_diario(year=2024, month=8)

        keys = {"label", "data", "borderRdius", "barThickness", "backgroundColor"}
        self.assertTrue(keys.issubset(resultados[0].keys()))
        self.assertTrue(keys.issubset(resultados[1].keys()))
        self.assertTrue(keys.issubset(resultados[2].keys()))

        self.assertEquals(len(resultados), 4)

        self.assertEquals(len(resultados[0]["data"]), 3)
        self.assertEquals(len(resultados[1]["data"]), 3)
        self.assertEquals(len(resultados[2]["data"]), 3)

        self.assertIsInstance(resultados[0]["data"], list)
        self.assertIsInstance(resultados[1]["data"], list)
        self.assertIsInstance(resultados[2]["data"], list)
        self.assertIsInstance(resultados[3], set)
        

        self.assertEquals(resultados[0]['data'][0], [0, 0])
        self.assertEquals(resultados[1]['data'][0], [0, 200.0])
        self.assertEquals(resultados[2]['data'][0], [0, 100.0])

    def test_venta_items_queryset__grafico_bar_montos_productos_vendidos_mensual(self):
        efectivo = MetodoPago.objects.get(nombre="Dinheiro")
        luz_70 = Producto.objects.get(nombre="luzeia 70gm")
        luz_120 = Producto.objects.get(nombre="luzeia 120gm")

        for venta in Venta.objects.all():
            UsoMetodoPago.objects.create(venta=venta, monto=venta.total, metodo=efectivo)
            VentaItem.objects.create(producto=luz_70, venta=venta, cantidad=2, precio=luz_70.precio)
            VentaItem.objects.create(producto=luz_120, venta=venta, cantidad=1, precio=luz_120.precio)
            
 
        resultados = VentaItem.objects.grafico_bar_montos_productos_vendidos_mensual(year=2024, month=8)

        self.assertEquals(1,1)
        self.assertEquals(len(resultados), 2)

        keys = {"label", "data", "borderRdius", "barThickness", "backgroundColor"}
        self.assertEquals(len(resultados[0]), len(keys))
        self.assertEquals(len(resultados[1]), len(keys))
        
        self.assertTrue(keys.issubset(resultados[0].keys()))
        self.assertTrue(keys.issubset(resultados[1].keys()))

        self.assertEquals(resultados[0]['data'], [560])
        self.assertEquals(resultados[1]['data'], [700])


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

    def test_producto_queryset__produccion_al_mes(self):
        resultado = Producto.objects.produccion_al_mes_progress_chart(year=2024, month=8)
        # print(resultado)
      

        self.assertEquals(1,1)


