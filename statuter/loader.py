from __future__ import unicode_literals
from xml.sax import make_parser, handler
from statuter.block import Page, Word, Character


class RscLoader(handler.ContentHandler):

    def __init__(self, page_number):
        handler.ContentHandler.__init__(self)
        self._page_number = str(page_number)
        self.page = None
        self._on_current_page = False
        self._current_word = None
        self._current_character = None

    def startElement(self, name, attrs):
        if name == 'page' and attrs.get('id') == self._page_number:
            self._on_current_page = True
            left, bottom, right, top = self._extract_bbox(attrs['bbox'])
            self.page = Page(left, right, bottom, top)

        if self._on_current_page is True and name == 'text':
            left, bottom, right, top = self._extract_bbox(attrs['bbox'])
            self._current_character = Character(left, right, bottom, top, size=attrs['size'], font=attrs['font'])

    def characters(self, content):
        if self._current_character is not None:
            self._current_character.text = content

    def endElement(self, name):
        if name == 'page':
            self._on_current_page = False

        if self.page is not None and name == 'text':
            if self._current_word is None:
                self._current_word = Word()
                self.page.add_word(self._current_word)

            if self._current_word.add_character(self._current_character):
                self._current_character = None
            else:
                self._current_word = Word()
                self.page.add_word(self._current_word)
                self._current_word.add_character(self._current_character)
                self._current_character = None


    # returns a tuple of (left, bottom, right, top)
    def _extract_bbox(self, bbox):
        return [float(x) for x in bbox.split(',')]


def get_page(path, page_number):
    parser = make_parser()
    content_loader = RscLoader(page_number)
    parser.setContentHandler(content_loader)

    parser.parse(path)

    content_loader.page.compute_column_margins()
    content_loader.page.remove_troublesome_lines()
    return content_loader.page
