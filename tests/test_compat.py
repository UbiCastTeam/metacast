'''
MetaCast - Compatibility test, import and export in older formats.
'''
from io import StringIO
from pathlib import Path

import pytest

from metacast import io as mcio

SAMPLES_DIR = Path(__file__).resolve().parent / 'samples'


@pytest.mark.parametrize('load_fct, dump_fct, extension, expected_start', [
    pytest.param(mcio.load_xml, mcio.dump_xml, 'xml', '<', id='xml'),
    pytest.param(mcio.load_json, mcio.dump_json, 'json', '{', id='json'),
    # The JS functions are not tested as they use same code as json
])
@pytest.mark.parametrize('sample', ['sample_2.1', 'sample_2.6_A', 'sample_2.6_B'])
def test_explicit(load_fct, dump_fct, extension, expected_start, sample):
    path = SAMPLES_DIR / f'{sample}.{extension}'
    content = path.read_text()
    mc = load_fct(content)
    result = dump_fct(mc)
    assert result.startswith(expected_start)

    updated_path = SAMPLES_DIR / f'{sample}_updated.{extension}'
    updated_content = updated_path.read_text()
    assert result == updated_content


@pytest.mark.parametrize('extension', ['xml', 'json'])
@pytest.mark.parametrize('sample', ['sample_2.1', 'sample_2.6_A', 'sample_2.6_B'])
def test_automatic(extension, sample):
    path = SAMPLES_DIR / f'{sample}.{extension}'
    mc = mcio.load(path)
    buf = StringIO()
    buf.name = path.name
    mcio.dump_file(mc, buf)
    result = buf.getvalue()
    assert isinstance(result, str)

    buf.seek(0)
    mc = mcio.load_file(buf)
    buf2 = StringIO()
    buf2.name = path.name
    mcio.dump_file(mc, buf2)
    result2 = buf.getvalue()
    assert result2 == result
