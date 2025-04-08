from django import template

register = template.Library()

@register.filter
def format_phone(value):
    """Format a 10-digit phone number as (XXX)-XXX-XXXX"""
    if not value:
        return value
    value = ''.join(filter(str.isdigit, str(value)))
    if len(value) == 10:
        return f"({value[:3]})-{value[3:6]}-{value[6:]}"
    return value 