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