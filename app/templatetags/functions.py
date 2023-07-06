from django import template
from app.models import TmdbApi

register = template.Library()
url=TmdbApi.original_images_url

@register.simple_tag
def get_image_path(path):
    return url + path

@register.filter
def replace(value):
    return value.replace(" ", "")