from core.models import (
    TipoGuarana,
    Saco,
    Produccion,
    Producto,
    ProduccionDetalle,
    Ralada,
    MetodoPago,
    Venta,
    VentaItem,
    UsoMetodoPago
)
# run the command: python manage.py runscript populate
def run():
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

    
    MetodoPago.objects.create(nombre="Visa Credito")
    MetodoPago.objects.create(nombre="Visa Debito")
    MetodoPago.objects.create(nombre="Mastercard Credito")
    MetodoPago.objects.create(nombre="Mastercard Debito")
    MetodoPago.objects.create(nombre="Pix", tipo=MetodoPago.Tipo.PIX)
    MetodoPago.objects.create(nombre="Dinheiro", tipo=MetodoPago.Tipo.EFECTIVO)

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


    pix = MetodoPago.objects.get(nombre="Pix")
    efectivo = MetodoPago.objects.get(nombre="Dinheiro")
    visa = MetodoPago.objects.get(nombre="Visa Debito")

    for i, venta in enumerate(Venta.objects.all(), 1):
        if i % 2 == 1:
            UsoMetodoPago.objects.create(venta=venta, monto=venta.total, metodo=pix)
            VentaItem.objects.create(producto=luz_70, venta=venta, cantidad=1, precio=luz_70.precio)
            VentaItem.objects.create(producto=maue_70, venta=venta, cantidad=1, precio=maue_70.precio)


        elif i % 3 == 0:
            UsoMetodoPago.objects.create(venta=venta, monto=venta.total, metodo=efectivo)
            VentaItem.objects.create(producto=luz_120, venta=venta, cantidad=1, precio=luz_120.precio)

        else:
            UsoMetodoPago.objects.create(venta=venta, monto=venta.total, metodo=visa)
            VentaItem.objects.create(producto=maue_200, venta=venta, cantidad=1, precio=maue_200.precio)
            VentaItem.objects.create(producto=maue_70, venta=venta, cantidad=1, precio=maue_70.precio)

