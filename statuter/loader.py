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
            self.page = Page(self._page_number, left, right, bottom, top)

        if self._on_current_page is True and name == 'text':
            left, bottom, right, top = self._extract_bbox(attrs['bbox'])
            self._current_character = Character(left, right, bottom, top, size=float(attrs['size']), font=attrs['font'])

    def characters(self, content):
        if self._current_character is not None:
            self._current_character.text = content

    def endElement(self, name):
        if name == 'page':
            self._on_current_page = False

        if self._on_current_page is True and name == 'text':
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


def extract_pages(input_path, english_output, french_output, pages):
    with open(english_output, 'w') as english_file:
        with open(french_output, 'w') as french_file:
            for page_no in pages:
                page = get_page(input_path, page_no)
                english_markdown = page.convert_to_markdown(page.english)
                english_file.write(english_markdown)

                french_markdown = page.convert_to_markdown(page.french)
                french_file.write(french_markdown)
                print "Finished page {}".format(page_no)
