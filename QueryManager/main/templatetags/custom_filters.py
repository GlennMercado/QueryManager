from django import template

register = template.Library()

@register.filter
def count_images(attachments):
    return sum(1 for attachment in attachments if attachment.is_image)