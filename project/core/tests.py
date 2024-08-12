from django.utils import timezone as tz
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from decimal import Decimal
from collections import defaultdict
import datetime
from core.models import (
    Venta,
    MetodoPago,
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

        resultados = Venta.objects.data_for_chartjs(year=2024, month=8)
        
        print(resultados)
        self.assertIn('11/08', resultados['fechas'])
        self.assertIn('12/08', resultados['fechas'])
        self.assertIn('13/08', resultados['fechas'])

        


# metodo_pago = models.ManyToManyField(MetodoPago, related_name="ventas")
            # nota = models.TextField(blank=True, null=True)
            # total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
            # fecha_venta = models.DateField(default=tz.now)
            # fecha_registro = models.DateTimeField(auto_now=True)
            # compra_vidros = models.ForeignKey("CompraVidros", related_name="venta", on_delete=models.SET_NULL, blank=True, null=True)

# from .models import Project, Testimonial
# from django.core.exceptions import ValidationError

# class ProjectMinimumRequirements(TestCase):
#     def test_project_creation_dosent_require_image(self):
#         project = Project.objects.create(
#             customer="some one",
#             customer_commercial_field="does some stuff",
#             description="some description"
#         )
#         self.assertIsInstance(project, Project)

# class ProjectImageFieldValidation(TestCase):
#     def setUp(self):
#         Project.objects.create(
#             customer="some one",
#             customer_commercial_field="does some stuff",
#             description="some description"
#         )

#     def test_project_creation_cannot_be_published_without_image(self):
#         project = Project.objects.first()
#         self.assertEquals(project.status, Project.Status.EDITING)

#         with self.assertRaises(ValidationError) as e: 
#             project.publish()

#         self.assertIn('image', e.exception.message_dict)
#         self.assertEqual(
#             e.exception.message_dict['image'],
#             ["For publishing you need to add an image."]
#         )

#     def test_project_creation_can_be_publishing_when_has_image(self):
#         project = Project.objects.first()
#         self.assertEquals(project.status, Project.Status.EDITING)

#         project.image = "the/path/to/some/image.jpg"
#         project.publish()
#         self.assertEquals(project.status, Project.Status.PUBLISHED)


# class TestimonialImageFieldValidation(TestCase):
#     def setUp(self):
#         Testimonial.objects.create(
#             name="some one",
#             profession="does some stuff",
#             message="some description"
#         )

#     def test_testimonial_creation_cannot_be_published_without_image(self):
#         testimonial = Testimonial.objects.first()
#         self.assertEquals(testimonial.status, Testimonial.Status.EDITING)

#         with self.assertRaises(ValidationError) as e: 
#             testimonial.publish()

#         self.assertIn('image', e.exception.message_dict)
#         self.assertEqual(
#             e.exception.message_dict['image'],
#             ["For publishing you need to add an image."]
#         )

#     def test_testimonial_creation_can_be_publishing_when_has_image(self):
#         testimonial = Testimonial.objects.first()
#         self.assertEquals(testimonial.status, Testimonial.Status.EDITING)

#         testimonial.image = "the/path/to/some/image.jpg"
#         testimonial.publish()
#         self.assertEquals(testimonial.status, Testimonial.Status.PUBLISHED)
