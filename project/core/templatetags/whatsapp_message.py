from django import template
from django.utils.safestring import mark_safe
import re
from urllib.parse import quote

register = template.Library()

@register.filter(name="whatsapp")
def scape_text(text):
    cadena = re.sub(r'\s+', ' ', text)
    return quote(cadena)