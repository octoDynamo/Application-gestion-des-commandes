from django import template

register = template.Library()

@register.filter
def is_director(user):
    return user.groups.filter(name='Directeurs').exists()
