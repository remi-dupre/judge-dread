"""
Configuration and personalisation of python-markdown.

This module defines loaded extensions from python-markdown, and creates some.
More documentation about python-markdown: https://python-markdown.github.io/
"""
from markdown import markdown

from .io_examples import IOExamples
from .attachments import AttachmentLinks


def load_markdown_module(attachment_url_writer=None):
    """
    Load markdown module with appropriate extensions.

    You might need to specify some parameters:
    :param attachment_url_writer: the function giving an attachment's url given
      its name.
    """
    loaded_extensions = [
        'markdown.extensions.smart_strong',
        'markdown.extensions.fenced_code',
        'markdown.extensions.footnotes',
        'markdown.extensions.tables',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'markdown.extensions.smarty'
    ]

    # Custom modules
    loaded_extensions.append(IOExamples())

    if attachment_url_writer is None:
        loaded_extensions.append(AttachmentLinks())
    else:
        # print(attachment_url_writer)
        loaded_extensions.append(
            AttachmentLinks(url_writer=attachment_url_writer)
        )

    return lambda text: markdown(text, extensions=loaded_extensions)