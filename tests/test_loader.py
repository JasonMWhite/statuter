import os
import pytest
from statuter import loader


@pytest.fixture
def content_path():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'tests/content_fixture.xml')


@pytest.fixture
def layout_path():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'tests/layout_fixture.xml')


def test_content(content_path):
    page = loader.get_page(content_path, 24)

    output = ' '.join([page.words[i].text for i in range(20, 40)])
    assert output == 'any description of vessel used in navigation and not propelled by oars ; &quot;surrogate judge&quot; means a surrogate judge in'


def test_compute_column_margins(layout_path):
    page = loader.get_page(layout_path, 24)
    assert page.compute_column_margins() == (30.7, 142.1, 149.4, 261.0)


def test_remove_top_lines(content_path):
    page = loader.get_page(content_path, 24)
    page.compute_column_margins()

    top_ten_words = [w.text for w in page.words[0:10]]
    bottom_ten_words = [w.text for w in page.words[-10:]]

    assert 'Chap.' in top_ten_words
    assert 'A-l' in top_ten_words
    assert 'Amiraute' in top_ten_words
    assert 'Chap.' in bottom_ten_words
    assert 'A-l' in bottom_ten_words
    assert 'Amiraute' in bottom_ten_words

    page.remove_troublesome_lines()

    top_ten_words = [w.text for w in page.words[0:10]]
    bottom_ten_words = [w.text for w in page.words[-10:]]

    assert 'Chap.' not in top_ten_words
    assert 'A-1' not in top_ten_words
    assert 'Amiraute' not in top_ten_words
    assert 'Chap.' not in bottom_ten_words
    assert 'A-l' not in bottom_ten_words
    assert 'Amiraute' not in bottom_ten_words
