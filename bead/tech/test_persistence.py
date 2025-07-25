# coding: utf-8
import pytest
from . import persistence as m


def get_structure():
    return {
        '1': 'árvíztűrő',
        'a': 'tükörfúrógép',
        'z': [1, '', 3.14, {}]
    }


def test_streams(tmp_path):
    """Test persistence through file streams."""
    # given a persisted structure as a file
    file_path = tmp_path / 'file'
    with open(file_path, 'w') as f:
        m.dump(get_structure(), f)
    
    # when file is read back
    with open(file_path, 'r') as f:
        structure = m.load(f)
    
    # then it equals the original structure
    assert get_structure() == structure


def test_strings():
    """Test persistence through strings."""
    # given a persisted structure as a string
    string = m.dumps(get_structure())
    
    # when string is parsed back
    structure = m.loads(string)
    
    # then it equals the original structure
    assert get_structure() == structure
