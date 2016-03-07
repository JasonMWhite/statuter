import io
import os
import re
import string


class Character(object):
    def __init__(self, left, right, bottom, top, text='', size=5.0, font='Courier'):
        self.text = text
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.size = size
        self.font = font

    @property
    def height(self):
        return self.top - self.bottom


class Word(object):

    MAX_HORIZONTAL_OVERLAP = 0.01
    MAX_HORIZONTAL_SPACING = 0.01
    MIN_VERTICAL_OVERLAP_FRACTION = 0.95

    def __init__(self):
        self._characters = []

    def add_character(self, character):
        if self.can_add(character):
            self._characters.append(character)
            return True
        else:
            return False

    def vertical_overlap_fraction(self, chararacter):
        intersection_length = min(self.top, chararacter.top) - max(self.bottom, chararacter.bottom)
        return max(intersection_length / self.height, intersection_length / chararacter.height)

    def can_add(self, character):
        return self._characters == [] or \
               (-self.MAX_HORIZONTAL_OVERLAP <= (character.left - self.right) <= self.MAX_HORIZONTAL_SPACING and
                self.vertical_overlap_fraction(character) >= self.MIN_VERTICAL_OVERLAP_FRACTION)

    @property
    def text(self):
        return ''.join([char.text for char in self._characters])

    @property
    def num_chars(self):
        return len(self._characters)

    @property
    def left(self):
        return min([char.left for char in self._characters])

    @property
    def right(self):
        return max([char.right for char in self._characters])

    @property
    def top(self):
        return max([char.top for char in self._characters])

    @property
    def bottom(self):
        return min([char.bottom for char in self._characters])

    @property
    def height(self):
        return self.top - self.bottom

    @property
    def mean_size(self):
        total_size = sum([char.size for char in self._characters])
        return total_size / len(self._characters)

    @property
    def fraction_capitalized(self):
        caps = [char for char in self._characters if char.text in string.ascii_uppercase]
        non_caps = [char for char in self._characters if char.text in string.ascii_lowercase]
        total = len(caps) + len(non_caps)
        if total == 0:
            return 1.0
        else:
            return float(len(caps)) / total

    @property
    def mode_font(self):
        fonts = {}
        for char in self._characters:
            fonts[char.font] = fonts.get(char.font, 0) + 1

        font, _ = sorted(fonts.items(), key=lambda f: (-f[1], f[0]))[0]
        return font

    def __repr__(self):
        return self.text


class Page(object):

    MIN_MARGIN = 10.0
    HEADER_CAP_THRESHOLD = 0.9
    HEADER_1_THRESHOLD_SIZE = 7.5
    HEADER_2_THRESHOLD_SIZE = 4.9
    GAP_RANGE_FRACTION = 0.2

    def __init__(self, page_no, left, right, bottom, top):
        self.words = []
        self.page_no = page_no
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.sweep_lines = {x: 0 for x in self._increment_by_point_one(self.left, self.right)}
        self.left_edge, self.right_edge = None, None
        self.left_gap_edge, self.right_gap_edge = None, None

    def add_words(self, words):
        self.words.extend(words)

    def add_word(self, word):
        self.words.append(word)

    @property
    def text_bottom(self):
        return min([w.bottom for w in self.words])

    @property
    def text_top(self):
        return max([w.top for w in self.words])

    @property
    def text_left(self):
        return min([w.left for w in self.words])

    @property
    def text_right(self):
        return max([w.right for w in self.words])

    def _increment_by_point_one(self, left, right):
        return [x / 10.0 for x in range(int(round(left, 1) * 10), int(round(right, 1) * 10 + 1))]

    def _vertical_range_adjustment(self):
        distinct_lines = sorted(set([word.bottom for word in self.words]))
        range_adjustment = min(len(distinct_lines) * 0.25, 10)
        return distinct_lines[range_adjustment], distinct_lines[-range_adjustment]

    def _compute_vertical_lines(self):
        bottom, top = self._vertical_range_adjustment()

        middle_words = [w for w in self.words if w.bottom >= bottom and w.bottom <= top]
        for word in middle_words:
            for entry in self._increment_by_point_one(word.left, word.right):
                self.sweep_lines[entry] += 1

    def _middle_gap(self):
        left = self.text_left
        right = self.text_right
        midpoint = (right - left) / 2
        sweep_range = (right - left) * self.GAP_RANGE_FRACTION / 2
        sweep_left, sweep_right = midpoint - sweep_range, midpoint + sweep_range

        left_edge, right_edge = None, None
        for pt in self._increment_by_point_one(sweep_left, sweep_right):
            if self.sweep_lines[pt] == 0:
                if left_edge is None:
                    left_edge = pt
                right_edge = pt
            elif self.sweep_lines[pt] != 0 and left_edge is not None:
                break

        assert left_edge is not None and right_edge is not None, "Couldn't find middle gap on page {}".format(self.page_no)
        return left_edge, right_edge

    def _left_margin(self, gap_edge):
        margin = self.left
        for pt in self._increment_by_point_one(self.left, gap_edge):
            if self.sweep_lines[pt] == 0 and pt != gap_edge:
                margin = pt
        return margin

    def _right_margin(self, gap_edge):
        margin = gap_edge
        for pt in self._increment_by_point_one(gap_edge, self.right):
            if self.sweep_lines[pt] == 0 and pt != gap_edge:
                margin = pt
                break
        return margin

    def compute_column_margins(self):
        self._compute_vertical_lines()
        self.left_gap_edge, self.right_gap_edge = self._middle_gap()
        self.left_edge = self._left_margin(self.left_gap_edge)
        self.right_edge = self._right_margin(self.right_gap_edge)
        return self.left_edge, self.left_gap_edge, self.right_gap_edge, self.right_edge

    def remove_troublesome_lines(self):
        troublesome_words = []
        bottom, top = self._vertical_range_adjustment()

        for w in self.words:
            if w.left <= self.right_gap_edge and w.right >= self.left_gap_edge:
                troublesome_words.append(w)

        if len(troublesome_words) > 0:
            highest_words = [w.bottom for w in troublesome_words if w.bottom >= top]
            lowest_words = [w.top for w in troublesome_words if w.bottom <= bottom]

            words_to_remove = []
            for word in self.words:
                if len(highest_words) > 0 and word.top > min(highest_words):
                    words_to_remove.append(word)
                if len(lowest_words) > 0 and word.bottom < max(lowest_words):
                    words_to_remove.append(word)

            for word in words_to_remove:
                self.words.remove(word)

    def _extract_language(self, left, right):
        language_words = [word for word in self.words if word.left > left and word.right < right]
        language_words.sort(key=lambda word: (-word.bottom, word.left))

        line = Line()
        lines = []

        for word in language_words:
            if not line.add_word(word):
                line.sort_words()
                lines.append(line)
                line = Line()
                line.add_word(word)

        if len(line.words) != 0:
            line.sort_words()
            lines.append(line)

        return lines

    @property
    def english(self):
        return self._extract_language(self.left_edge, self.left_gap_edge)

    @property
    def french(self):
        return self._extract_language(self.right_gap_edge, self.right_edge)

    def _check_header(self, line_text):
        header_match = re.search(r'^(\d+\.)(.*)', line_text)
        if header_match:
            line_text = os.linesep + '**{}**{}'.format(*header_match.group(1, 2))
        return line_text

    def _check_letter_paragraph(self, line_text):
        letter_match = re.search(r'^^\(([a-z]+)\)( .*)', line_text)
        if letter_match:
            line_text = '  * (_{}_){}'.format(*letter_match.group(1, 2))
        return line_text

    def _convert_line_to_markdown(self, line):
        prefix = ''
        markdown_text = line.text
        markdown_text = markdown_text.replace('_', ' ')
        markdown_text = markdown_text.replace('&quot;', '"')

        if all([word.fraction_capitalized >= self.HEADER_CAP_THRESHOLD for word in line.words]):
            if line.mean_size >= self.HEADER_1_THRESHOLD_SIZE:
                prefix = '# '
            elif line.mean_size >= self.HEADER_2_THRESHOLD_SIZE:
                prefix = '## '

        if prefix == '':
            markdown_text = self._check_header(markdown_text)
            markdown_text = self._check_letter_paragraph(markdown_text)
        else:
            prefix = os.linesep + prefix

        return prefix + markdown_text

    def convert_to_markdown(self, lines):
        markdown_buffer = io.StringIO()
        for line in lines:
            markdown_line = self._convert_line_to_markdown(line)
            markdown_buffer.write(markdown_line + os.linesep)
        output = markdown_buffer.getvalue()
        markdown_buffer.close()
        return output


class Line(object):

    MIN_VERTICAL_OVERLAP_FRACTION = 0.5

    def __init__(self):
        self.words = []

    def add_word(self, word):
        if self.can_add(word):
            self.words.append(word)
            return True
        else:
            return False

    def vertical_overlap(self, word):
        intersection_length = min(self.top, word.top) - max(self.bottom, word.bottom)
        return max(intersection_length / self.height, intersection_length / word.height)

    def can_add(self, word):
        return self.words == [] or \
            self.vertical_overlap(word) >= self.MIN_VERTICAL_OVERLAP_FRACTION

    @property
    def left(self):
        return min([word.left for word in self.words])

    @property
    def right(self):
        return max([word.right for word in self.words])

    @property
    def bottom(self):
        return min([word.bottom for word in self.words])

    @property
    def top(self):
        return max([word.top for word in self.words])

    @property
    def height(self):
        return self.top - self.bottom

    @property
    def mean_size(self):
        weighted_size = sum([word.num_chars * word.mean_size for word in self.words])
        total_size = sum([word.num_chars for word in self.words])
        return weighted_size / total_size

    @property
    def mode_font(self):
        fonts = {}
        for word in self.words:
            fonts[word.mode_font] = fonts.get(word.mode_font, 0) + word.num_chars

        font, _ = sorted(fonts.items(), key=lambda f: (-f[1], f[0]))[0]
        return font

    @property
    def text(self):
        return ' '.join([word.text for word in self.words])

    def sort_words(self):
        self.words.sort(key=lambda word: word.left)

    def __repr__(self):
        data = ' '.join([word.text for word in self.words])
        return "<Line text='{}'>".format(data)
