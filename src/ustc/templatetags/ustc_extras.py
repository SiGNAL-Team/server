from django import template
from django.utils.translation import get_language

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


@register.filter
def translated_name(obj):
    """Get the translated name based on current language"""
    if not obj:
        return ""

    current_language = get_language()

    # Check if object has name_cn and name_en attributes
    if hasattr(obj, 'name_cn') and hasattr(obj, 'name_en'):
        if current_language == 'zh-cn':
            return obj.name_cn or obj.name_en or str(obj)
        else:
            return obj.name_en or obj.name_cn or str(obj)

    # Fallback to string representation
    return str(obj)


@register.filter
def translated_course_name(obj):
    """Get the translated course name based on current language"""
    if not obj:
        return ""

    current_language = get_language()

    # Check if object has name_cn and name_en attributes
    if hasattr(obj, 'name_cn') and hasattr(obj, 'name_en'):
        if current_language == 'zh-cn':
            return obj.name_cn or obj.name_en or str(obj)
        else:
            return obj.name_en or obj.name_cn or str(obj)

    # Fallback to string representation
    return str(obj)


@register.filter
def mul(value, arg):
    """Multiply value by arg"""
    try:
        return value * arg
    except (TypeError, ValueError):
        return ""


@register.simple_tag
def get_language_name():
    """Get current language name for display"""
    current_language = get_language()
    language_names = {
        'zh-cn': '简体中文',
        'en': 'English'
    }
    return language_names.get(current_language, current_language)
