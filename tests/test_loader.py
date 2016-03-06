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
    assert output == 'vessel used in navigation and not propelled by oars ; &quot;surrogate judge&quot; means a surrogate judge in Admiralty of the'


def test_compute_column_margins(layout_path):
    page = loader.get_page(layout_path, 24)
    assert page.compute_column_margins() == (30.7, 142.1, 149.4, 261.0)


def test_remove_top_lines(content_path):
    page = loader.get_page(content_path, 24)
    top_ten_words = [w.text for w in page.words[0:10]]
    bottom_ten_words = [w.text for w in page.words[-10:]]

    assert 'Chap.' not in top_ten_words
    assert 'A-1' not in top_ten_words
    assert 'Amiraute' not in top_ten_words
    assert 'Chap.' not in bottom_ten_words
    assert 'A-l' not in bottom_ten_words
    assert 'Amiraute' not in bottom_ten_words
    assert len(page.words) == 761


def test_languages(content_path):
    page = loader.get_page(content_path, 24)

    assert page.english[0].text == 'President or a puisne judge of that Court ;'
    assert len(page.english) == 43

    assert page.french[0].text == 'amiraute de la Cour de 1 Echiquier, nomme'
    assert len(page.french) == 52


def test_convert_to_markdown(content_path):
    page = loader.get_page(content_path, 24)
    english = page.english[6:9]
    markdown = page.convert_to_markdown(english)
    assert markdown == '## CONSTITUTION OF COURT\n**3.** (1) The Exchequer Court of Canada\ncontinues to be a Court of Admiralty and to\n'
