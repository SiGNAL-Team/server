from django import template

register = template.Library()

@register.filter
def getattr(obj, attr):
    """Gets an attribute of an object dynamically from a string name"""
    try:
        if '__' in attr:
            # For nested attributes like 'course__name_cn'
            parts = attr.split('__')
            for part in parts[:-1]:
                obj = getattr(obj, part)
            return getattr(obj, parts[-1])
        return getattr(obj, attr)
    except:
        return ""
