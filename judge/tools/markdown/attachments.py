"""
Definition of semantic for links to local attachments.

An attachment is a local file, that can be identified by its name, and
  downloaded from a different url.
The syntax to insert an attached image in the markdown is:
    ![image title]{image name}
The syntax to insert a link to an attached file is
    [attachment text]{attachment name}

When the module is loaded you might want to specify a function to write an
  url given an attachment's name. You can specify this with the parameter
  url_writer: `AttachmentLinks(url_writer=lambda name: 'baseurl/' + name)`
"""
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree


def default_url_writer(attachment_name):
    """
    Default engine to write attachment url, given its name.

    This default engine will behave like a default url handling.
    """
    return attachment_name


class AttachmentLinksPattern(Pattern):
    PATTERN = r'\[([^\[]*)\]{([^}]*)}'

    def __init__(self, url_writer, **kwargs):
        self.url_writer = url_writer
        super(AttachmentLinksPattern, self).__init__(self.PATTERN, **kwargs)

    def handleMatch(self, match):
        attachment_name = match.group(3)
        attachment_text = match.group(2)
        attachment_url = self.url_writer(attachment_name)

        if not attachment_text:
            attachment_text = attachment_name

        link = etree.Element('a')
        link.text = attachment_text
        link.set('href', attachment_url)
        return link


class AttachmentImagePattern(Pattern):
    PATTERN = r'!\[([^\[]*)\]{([^}]*)}'

    def __init__(self, url_writer, **kwargs):
        self.url_writer = url_writer
        super(AttachmentImagePattern, self).__init__(self.PATTERN, **kwargs)

    def handleMatch(self, match):
        attachment_name = match.group(3)
        attachment_title = match.group(2)
        attachment_url = self.url_writer(attachment_name)

        image = etree.Element('img')
        image.set('src', attachment_url)
        image.set('title', attachment_title)
        return image


class AttachmentLinks(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'url_writer' : [
                default_url_writer,
                'The function giving the url of the pattern giving its name'
            ]
        }
        super(AttachmentLinks, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.inlinePatterns.add(
            'attachment_link',
            AttachmentLinksPattern(self.getConfig('url_writer')),
            '>link'
        )
        md.inlinePatterns.add(
            'attachment_image',
            AttachmentImagePattern(self.getConfig('url_writer')),
            '<attachment_link'
        )
