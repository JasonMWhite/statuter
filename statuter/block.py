class Character(object):
    def __init__(self, text, left, right, bottom, top, size=5.0, font='Courier'):
        self.text = text
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.size = size
        self.font = font


class Word(object):
    def __init__(self, character):
        self._characters = [character]

    def add_character(self, character):
        self._characters.append(character)

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


class Line(object):
    def __init__(self, word):
        self._words = [word]

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