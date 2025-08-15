import pytest
from dashboard_insights_agentic_system.dynamic_pipeline.extractors.dashboard_extractor import DashboardExtractor

class DummyOCR:
    def __init__(self):
        pass

@pytest.fixture
def extractor():
    return DashboardExtractor(ocr_helper=DummyOCR())

def test_fail_result_returns_expected_schema(extractor):
    result = extractor._fail_result('powerbi', 'private', 'error msg')
    assert result['status'] == 'failed'
    assert result['source'] == 'powerbi'
    assert result['auth_type'] == 'private'
    assert result['tables'] == []
    assert result['kpis'] == []
    assert result['filters'] == []
    assert result['visuals'] == []
    assert result['layout'] == {}
    assert result['components'] == []
    assert result['html_text'] == ''
    assert result['error'] == 'error msg'

def test_ensure_unified_schema_adds_highlights(extractor):
    input_result = {
        'status': 'success',
        'tables': [],
        'kpis': [],
        'filters': [],
        'visuals': [],
        'layout': {},
        'components': [{'type': 'table', 'rows': [[1,2]], 'headers': ['a','b']}],
        'html_text': 'text',
        'drill_state': {'foo': 'bar'},
        'error': None
    }
    unified = extractor._ensure_unified_schema(input_result, 'powerbi', 'private', {'foo': 'bar'})
    assert unified['status'] == 'success'
    assert unified['source'] == 'powerbi'
    assert unified['auth_type'] == 'private'
    assert unified['components'][0]['highlights'] == []
    assert unified['drill_state'] == {'foo': 'bar'}
    assert unified['html_text'] == 'text'
    assert unified['error'] is None

def test_extract_dashboard_fail(monkeypatch, extractor):
    def fail_connect_bi_dashboard(*args, **kwargs):
        return {'status': 'failed', 'error': 'connect error'}
    monkeypatch.setattr('dashboard_insights_agentic_system.dynamic_pipeline.extractors.dashboard_extractor.connect_bi_dashboard', fail_connect_bi_dashboard)
    result = extractor.extract_dashboard('powerbi', 'private')
    assert result['status'] == 'failed'
    assert result['error'] == 'connect error'
