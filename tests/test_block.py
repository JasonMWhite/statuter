import pytest
from statuter.block import Character, Word, Line


class TestCharacter(object):

    def test_init(self):
        character = Character('foo', 1.0, 2.0, 10.0, 11.0)
        assert character.text == 'foo'
        assert character.left == 1.0
        assert character.right == 2.0
        assert character.bottom == 10.0
        assert character.top == 11.0
        assert character.size == 5.0
        assert character.font == 'Courier'


class TestWord(object):

    @pytest.fixture
    def char_f(self):
        return Character('f', 1.0, 1.1, 10.0, 10.5, size=5.0)

    @pytest.fixture
    def char_o(self):
        return Character('o', 1.1, 1.2, 10.01, 10.51, size=5.5)

    @pytest.fixture
    def simple_word(self, char_f, char_o):
        w = Word(char_f)
        w.add_character(char_o)
        return w

    def test_text(self, simple_word):
        assert simple_word.text == 'fo'

    def test_num_chars(self, simple_word):
        assert simple_word.num_chars == 2

    def test_boundaries(self, simple_word):
        assert simple_word.left == 1.0
        assert simple_word.right == 1.2
        assert simple_word.top == 10.51
        assert simple_word.bottom == 10.0

    def test_mean_size(self, simple_word):
        assert simple_word.mean_size == 5.25

    def test_mode_font(self, simple_word):
        assert simple_word.mode_font == 'Courier'


class TestLine(object):

    @pytest.fixture
    def first_word(self):
        w = Word(Character('f', 1.0, 1.1, 10.0, 11.0, size=5.0, font='Courier'))
        w.add_character(Character('o', 1.1, 1.2, 10.0, 11.0, size=5.2, font='Courier'))
        w.add_character(Character('o', 1.2, 1.3, 10.0, 11.01, size=5.0, font='Arial'))
        return w

    @pytest.fixture
    def second_word(self):
        w = Word(Character('b', 1.4, 1.5, 10.0, 11.0, size=5.0, font='Courier'))
        w.add_character(Character('a', 1.5, 1.6, 10.0, 11.0, size=5.2, font='Courier'))
        w.add_character(Character('r', 1.6, 1.7, 10.01, 11.0, size=5.1, font='Arial'))
        w.add_character(Character('s', 1.7, 1.8, 10.0, 11.0, size=5.2, font='Arial'))
        return w

    @pytest.fixture
    def line(self, first_word, second_word):
        test_line = Line(first_word)
        test_line.add_word(second_word)
        return test_line

    def test_boundaries(self, line):
        assert line.left == 1.0
        assert line.right == 1.8
        assert line.top == 11.01
        assert line.bottom == 10.0

    def test_mean_size(self, line):
        assert round(line.mean_size, 2) == 5.1

    def test_mode_font(self, line):
        assert line.mode_font == 'Arial'

    def test_text(self, line):
        assert line.text == 'foo bars'
