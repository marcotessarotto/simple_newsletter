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
