import pytest
import types
import sys

# Import the data_cleaning module
import dashboard_insights_agentic_system.dynamic_pipeline.utils.data_cleaning as data_cleaning

def test_clean_component_adds_highlights():
    comp = {'type': 'table', 'rows': [[1,2]], 'headers': ['a','b']}
    cleaned = data_cleaning.clean_component(comp)
    assert 'highlights' in cleaned
    assert isinstance(cleaned['highlights'], list)

def test_clean_dashboard_preserves_fields():
    dashboard = {
        'tables': [{'headers': ['a'], 'rows': [[1]]}],
        'kpis': [{'name': 'k1', 'value': 1}],
        'filters': [{'type': 'dropdown', 'options': ['x']}],
        'visuals': [{'type': 'image', 'src': 'url'}],
        'layout': {'sections': ['s1']},
        'components': [{'type': 'table', 'rows': [[1]], 'headers': ['a']}],
        'html_text': 'text',
        'drill_state': {'foo': 'bar'},
        'error': None
    }
    cleaned = data_cleaning.clean_dashboard(dashboard)
    assert 'tables' in cleaned
    assert 'kpis' in cleaned
    assert 'filters' in cleaned
    assert 'visuals' in cleaned
    assert 'layout' in cleaned
    assert 'components' in cleaned
    assert 'html_text' in cleaned
    assert 'drill_state' in cleaned
    assert 'error' in cleaned
    for comp in cleaned['components']:
        assert 'highlights' in comp

def test_clean_dashboard_handles_missing_fields():
    dashboard = {}
    cleaned = data_cleaning.clean_dashboard(dashboard)
    assert isinstance(cleaned, dict)
    # Should not raise error even if fields are missing

# Add more tests as needed for edge cases
