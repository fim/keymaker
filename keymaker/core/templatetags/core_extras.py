from django import template

register = template.Library()

@register.filter
def tohex(value):
    """Return repr in hex"""
    try:
        value = int(value)
    except TypeError:
        return "Unrecognized Number"

    return "%x" % value

@register.filter
def tohexpair(value):
    """Return hex in couples"""
    hval = tohex(value)
    return ':'.join([hval[i:i+2] for i in range(0, len(hval),2)])
