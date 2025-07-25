import pytest
from .box import Box
from .tech.fs import write_file, rmtree
from .tech.timestamp import time_from_user
from .workspace import Workspace
from . import spec as bead_spec


@pytest.fixture
def box(temp_dir):
    """Create a test box with sample beads."""
    box = Box('test', temp_dir)

    def add_bead(name, kind, freeze_time):
        ws = Workspace(temp_dir / name)
        ws.create(kind)
        box.store(ws, freeze_time)

    add_bead('bead1', 'test-bead1', '20160704T000000000000+0200')
    add_bead('bead2', 'test-bead2', '20160704T162800000000+0200')
    add_bead('BEAD3', 'test-bead3', '20160704T162800000001+0200')
    return box


@pytest.fixture
def timestamp():
    """Provide a test timestamp."""
    return time_from_user('20160704T162800000000+0200')




def test_all_beads(box):
    """Test that all beads are returned."""
    bead_names = set(b.name for b in box.all_beads())
    assert set(['bead1', 'bead2', 'BEAD3']) == bead_names


def test_find_names(box, timestamp):
    """Test finding beads by name."""
    result = box.find_names(kind='test-bead1', content_id='', timestamp=timestamp)
    exact_match, best_guess, best_guess_timestamp, names = result

    assert exact_match is None
    assert 'bead1' == best_guess
    assert best_guess_timestamp is not None
    names_set = set(names)
    assert set(['bead1']) == names_set


def test_find_names_works_even_with_removed_box_directory(box, timestamp):
    """Test that find_names handles missing box directory gracefully."""
    rmtree(box.directory)
    result = box.find_names(kind='test-bead1', content_id='', timestamp=timestamp)
    exact_match, best_guess, best_guess_timestamp, names = result
    assert exact_match is None
    assert best_guess is None
    assert best_guess_timestamp is None
    names_list = list(names)
    assert [] == names_list


def test_find_with_uppercase_name(box, timestamp):
    """Test finding beads with uppercase names."""
    matches = box.get_context(bead_spec.BEAD_NAME, 'BEAD3', timestamp)
    best_name = matches.best.name
    assert 'BEAD3' == best_name


def test_box_methods_tolerate_junk_in_box(tmp_path_factory):
    """Test that box methods work even with junk files present."""
    temp_dir = tmp_path_factory.mktemp("box_junk")
    box = Box('test', temp_dir)

    def add_bead(name, kind, freeze_time):
        ws = Workspace(temp_dir / name)
        ws.create(kind)
        box.store(ws, freeze_time)

    add_bead('bead1', 'test-bead1', '20160704T000000000000+0200')
    add_bead('bead2', 'test-bead2', '20160704T162800000000+0200')
    add_bead('BEAD3', 'test-bead3', '20160704T162800000001+0200')
    
    # add junk
    junk_file = box.directory / 'some-non-bead-file'
    write_file(junk_file, 'random bits')
    
    bead_names = set(b.name for b in box.all_beads())
    assert set(['bead1', 'bead2', 'BEAD3']) == bead_names
