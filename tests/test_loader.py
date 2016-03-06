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


def test_column_margins(layout_path):
    page = loader.get_page(layout_path, 24)
    assert page.column_margins() == (30.7, 142.1, 149.4, 261.0)
