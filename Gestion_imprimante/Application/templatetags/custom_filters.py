from django import template

register = template.Library()

@register.filter
def is_director(user):
    return user.groups.filter(name='Directeurs').exists()

@register.filter
def is_assistant(user):
    return user.groups.filter(name='Assistants').exists()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def default_zero(value):
    return value if value is not None else 0

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])
