from django import template

register = template.Library()


@register.filter(name="first_line")
def first_line(value):
    """
    Return the first 'char_limit' characters of the given text.
    """
    char_limit = 120
    return value[:char_limit] + "..." if len(value) > char_limit else value
