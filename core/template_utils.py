import random
import string

from django.template import Context, Template
from django.utils.safestring import mark_safe


def render_template_from_string(template_string, context=None):
    """
    Renders a template from a given string.

    :param template_string: The template content as a string.
    :param context: The context dictionary to render the template with.
    :return: The rendered template as a string.
    """
    context = context or {}
    template = Template(template_string)
    return mark_safe(template.render(Context(context)))


def get_rnd_str(length=8):
    # Define the character pool to include a-z, A-Z, and 0-9
    char_pool = string.ascii_letters + string.digits
    return ''.join(random.choices(char_pool, k=length))
