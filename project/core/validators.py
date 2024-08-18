from django.core.exceptions import ValidationError
from django.db.models import FileField

def for_published_status_require_image_not_none(
    status:str,
    image:FileField,
    str_published_status: str = 'P',
    name_image_field='image' 
) -> None:
    if status == str_published_status and not image:
        raise ValidationError({
            name_image_field:"For publishing you need to add an image."
        })
    
def produccion_detalle_must_weight_less_or_equal_than_ralada(
    lista_productos:list,
    limit_weight: int = 2000,
) -> None:
    weight_count = 0
    for producto in lista_productos:
        weight_count += producto.peso_producido
    if weight_count > limit_weight:
        raise ValidationError({
            "Os produtos porduzidos não podem pasar do peso ralado"
        })