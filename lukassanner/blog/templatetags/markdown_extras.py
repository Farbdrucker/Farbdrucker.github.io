from django import template
from django.template.defaultfilters import stringfilter

import markdown as md

register = template.Library()

extensions = ["markdown.extensions.fenced_code", "md_mermaid", "mdx_math"]


@register.filter
@stringfilter
def markdown(value):
    return md.markdown(value, extensions=extensions)
