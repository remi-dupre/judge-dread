"""
Template tags to manipulate languages.
"""

from django.conf import settings
from django import template

register = template.Library()


@register.filter
def lang_full_name(lang):
    """
    Given an language identifier, return its human-readable name.
    """
    if lang in settings.LANGUAGES:
        return settings.LANGUAGES[lang]
    else:
        return lang
