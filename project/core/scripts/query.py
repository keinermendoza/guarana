import pprint
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
# run the command: python manage.py runscript query
def run():
    pprint.pp(Producto.objects.cantidad_vendida_progress_chart(year=2024, month=8))
    print()
    pprint.pp(Producto.objects.produccion_al_mes_progress_chart(year=2024, month=8))
