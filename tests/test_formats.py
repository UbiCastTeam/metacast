'''
MetaCast - Compatibility test, import and export in older formats.
'''
from io import StringIO
from pathlib import Path

import pytest

from metacast import io as mcio


@pytest.mark.parametrize('load_fct, dump_fct, expected_start, files', [
    pytest.param(mcio.load_xml, mcio.dump_xml, '<', ['sample_1.xml', 'sample_2.xml', 'sample_3.xml'], id='xml'),
    pytest.param(mcio.load_json, mcio.dump_json, '{', ['sample_1.json', 'sample_2.json', 'sample_3.json'], id='json'),
    pytest.param(mcio.load_js, mcio.dump_js, '/', ['sample_1.js', 'sample_2.js', 'sample_3.js'], id='js'),
])
def test_explicit(load_fct, dump_fct, expected_start, files):
    base_path = Path(__file__).resolve().parent
    for name in files:
        path = base_path / name
        content = path.read_text()
        mc = load_fct(content)
        result = dump_fct(mc)
        assert result.startswith(expected_start)


@pytest.mark.parametrize('files', [
    pytest.param(['sample_1.xml', 'sample_2.xml', 'sample_3.xml'], id='xml'),
    pytest.param(['sample_1.json', 'sample_2.json', 'sample_3.json'], id='json'),
    pytest.param(['sample_1.js', 'sample_2.js', 'sample_3.js'], id='js'),
])
def test_automatic(files):
    base_path = Path(__file__).resolve().parent
    for name in files:
        path = base_path / name
        mc = mcio.load(path)
        buf = StringIO()
        buf.name = name
        mcio.dump_file(mc, buf)
        result = buf.getvalue()
        assert isinstance(result, str)

        buf.seek(0)
        mc = mcio.load_file(buf)
        buf2 = StringIO()
        buf2.name = name
        mcio.dump_file(mc, buf2)
        result2 = buf.getvalue()
        assert result2 == result
