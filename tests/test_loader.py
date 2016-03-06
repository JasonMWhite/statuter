import os
from statuter import loader


def test_content():
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'tests/content_fixture.xml')
    page = loader.get_page(path, 24)

    output = ' '.join([page.words[i].text for i in range(20, 40)])
    assert output == 'any description of vessel used in navigation and not propelled by oars ; &quot;surrogate judge&quot; means a surrogate judge in'
