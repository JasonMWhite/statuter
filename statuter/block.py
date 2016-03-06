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
    def mode_font(self):
        fonts = {}
        for char in self._characters:
            fonts[char.font] = fonts.get(char.font, 0) + 1

        font, _ = sorted(fonts.items(), key=lambda f: (-f[1], f[0]))[0]
        return font


class Page(object):

    def __init__(self, left, right, bottom, top):
        self.words = []
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self._lines = {x: 0 for x in self.increment_by_point_one(self.left, self.right)}

    def add_words(self, words):
        self.words.extend(words)

    def add_word(self, word):
        self.words.append(word)

    def increment_by_point_one(self, left, right):
        return [x / 10.0 for x in range(int(round(left, 1) * 10), int(round(right, 1) * 10 + 1))]

    def compute_vertical_lines(self):
        for word in self.words:
            for entry in self.increment_by_point_one(word.left, word.right):
                self._lines[entry] += 1


class Line(object):
    def __init__(self):
        self._words = []

    def add_word(self, word):
        self._words.append(word)

    @property
    def left(self):
        return min([word.left for word in self._words])

    @property
    def right(self):
        return max([word.right for word in self._words])

    @property
    def bottom(self):
        return min([word.bottom for word in self._words])

    @property
    def top(self):
        return max([word.top for word in self._words])

    @property
    def mean_size(self):
        weighted_size = sum([word.num_chars * word.mean_size for word in self._words])
        total_size = sum([word.num_chars for word in self._words])
        return weighted_size / total_size

    @property
    def mode_font(self):
        fonts = {}
        for word in self._words:
            fonts[word.mode_font] = fonts.get(word.mode_font, 0) + word.num_chars

        font, _ = sorted(fonts.items(), key=lambda f: (-f[1], f[0]))[0]
        return font

    @property
    def text(self):
        return ' '.join([word.text for word in self._words])
