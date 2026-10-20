from django import template

register = template.Library()

@register.filter
def cop(value):
    try: amount = int(value)
    except (TypeError, ValueError): amount = 0
    return "$" + f"{amount:,}".replace(",", ".")

@register.filter
def multiply(value, quantity):
    try: return int(value) * int(quantity)
    except (TypeError, ValueError): return 0
