import pytest
from statuter.block import Character, Word, Line, Page


class TestCharacter(object):

    @pytest.fixture
    def char(self):
        return Character(1.0, 2.0, 10.0, 11.0, text='f')

    def test_init(self, char):
        assert char.text == 'f'
        assert char.left == 1.0
        assert char.right == 2.0
        assert char.bottom == 10.0
        assert char.top == 11.0
        assert char.size == 5.0
        assert char.font == 'Courier'

    def test_height(self, char):
        assert char.height == 1.0


class TestWord(object):

    @pytest.fixture
    def char_f(self):
        return Character(1.0, 1.1, 10.0, 10.5, size=5.0, text='f')

    @pytest.fixture
    def char_o(self):
        return Character(1.1, 1.2, 10.01, 10.51, size=5.5, text='o')

    @pytest.fixture
    def simple_word(self, char_f, char_o):
        w = Word()
        w.add_character(char_f)
        w.add_character(char_o)
        return w

    def test_add_character(self, char_f, char_o):
        char_b = Character(1.2, 1.3, 10.4, 10.8, size=4.0, text='b')
        char_a = Character(1.25, 1.35, 10.0, 10.5, size=4.0, text='a')
        char_r = Character(1.15, 1.25, 10.0, 10.5, size=4.0, text='r')
        w = Word()
        assert w.add_character(char_f)
        assert w.add_character(char_o)
        assert not w.add_character(char_b)
        assert not w.add_character(char_a)
        assert not w.add_character(char_r)
        assert w.text == 'fo'

    def test_text(self, simple_word):
        assert simple_word.text == 'fo'

    def test_num_chars(self, simple_word):
        assert simple_word.num_chars == 2

    def test_boundaries(self, simple_word):
        assert simple_word.left == 1.0
        assert simple_word.right == 1.2
        assert simple_word.top == 10.51
        assert simple_word.bottom == 10.0

    def test_height(self, simple_word):
        assert round(simple_word.height, 2) == 0.51

    def test_vertical_overlap_fraction(self, simple_word):
        char1 = Character(1.2, 1.3, 10.1, 10.4, size=5.0, text='1')
        char2 = Character(1.2, 1.3, 9.9, 10.6, size=6.0, text='2')
        char3 = Character(1.2, 1.3, 10.51, 11.01, size=5.5, text='3')
        char4 = Character(1.2, 1.3, 10.26, 10.76, size=5.5, text='4')

        assert simple_word.vertical_overlap_fraction(char1) == 1.0
        assert simple_word.vertical_overlap_fraction(char2) == 1.0
        assert simple_word.vertical_overlap_fraction(char3) == 0
        assert simple_word.vertical_overlap_fraction(char4) == 0.5

    def test_mean_size(self, simple_word):
        assert simple_word.mean_size == 5.25

    def test_mode_font(self, simple_word):
        assert simple_word.mode_font == 'Courier'


class TestPage(object):

    def test_add_word(self):
        w1 = Word()
        w2 = Word()
        page = Page(0.0, 300.0, 0.0, 305.0)
        page.add_word(w1)
        page.add_word(w2)

        assert len(page.words) == 2
        assert page.left == 0.0
        assert page.right == 300.0
        assert page.bottom == 0.0
        assert page.top == 305.0


class TestLine(object):

    @pytest.fixture
    def first_word(self):
        w = Word()
        w.add_character(Character(1.0, 1.1, 10.0, 11.0, size=5.0, font='Courier', text='f'))
        w.add_character(Character(1.1, 1.2, 10.0, 11.0, size=5.2, font='Courier', text='o'))
        w.add_character(Character(1.2, 1.3, 10.0, 11.01, size=5.0, font='Arial', text='o'))
        return w

    @pytest.fixture
    def second_word(self):
        w = Word()
        w.add_character(Character(1.4, 1.5, 10.0, 11.0, size=5.0, font='Courier', text='b'))
        w.add_character(Character(1.5, 1.6, 10.0, 11.0, size=5.2, font='Courier', text='a'))
        w.add_character(Character(1.6, 1.7, 10.01, 11.0, size=5.1, font='Arial', text='r'))
        w.add_character(Character(1.7, 1.8, 10.0, 11.0, size=5.2, font='Arial', text='s'))
        return w

    @pytest.fixture
    def line(self, first_word, second_word):
        test_line = Line()
        test_line.add_word(first_word)
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

    def test_can_add(self, line):
        third_word = Word()
        third_word.add_character(Character(1.9, 2.0, 10.05, 11.05, size=5.2, font='Arial', text='z'))

        fourth_word = Word()
        fourth_word.add_character(Character(1.9, 2.0, 10.3, 11.3, size=5.2, font='Arial', text='z'))

        assert line.can_add(third_word)
        assert not line.can_add(fourth_word)

    def test_add_word(self, line):
        third_word = Word()
        third_word.add_character(Character(1.9, 2.0, 10.05, 11.05, size=5.2, font='Arial', text='z'))

        assert line.add_word(third_word)
        assert line.text == 'foo bars z'

        fourth_word = Word()
        fourth_word.add_character(Character(2.0, 2.1, 10.3, 11.3, size=5.2, font='Arial', text='z'))

        assert not line.can_add(fourth_word)
        assert line.text == 'foo bars z'
