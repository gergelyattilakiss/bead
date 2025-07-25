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


@pytest.fixture
def box_with_junk(temp_dir):
    """Create a test box with sample beads and junk files."""
    box = Box('test', temp_dir)

    def add_bead(name, kind, freeze_time):
        ws = Workspace(temp_dir / name)
        ws.create(kind)
        box.store(ws, freeze_time)

    add_bead('bead1', 'test-bead1', '20160704T000000000000+0200')
    add_bead('bead2', 'test-bead2', '20160704T162800000000+0200')
    add_bead('BEAD3', 'test-bead3', '20160704T162800000001+0200')
    
    # add junk
    write_file(box.directory / 'some-non-bead-file', 'random bits')
    return box


def test_all_beads(box):
    """Test that all beads are returned."""
    assert set(['bead1', 'bead2', 'BEAD3']) == set(b.name for b in box.all_beads())


def test_find_names(box, timestamp):
    """Test finding beads by name."""
    (
        exact_match, best_guess, best_guess_timestamp, names
    ) = box.find_names(kind='test-bead1', content_id='', timestamp=timestamp)

    assert exact_match is None
    assert 'bead1' == best_guess
    assert best_guess_timestamp is not None
    assert set(['bead1']) == set(names)


def test_find_names_works_even_with_removed_box_directory(box, timestamp):
    """Test that find_names handles missing box directory gracefully."""
    rmtree(box.directory)
    (
        exact_match, best_guess, best_guess_timestamp, names
    ) = box.find_names(kind='test-bead1', content_id='', timestamp=timestamp)
    assert exact_match is None
    assert best_guess is None
    assert best_guess_timestamp is None
    assert [] == list(names)


def test_find_with_uppercase_name(box, timestamp):
    """Test finding beads with uppercase names."""
    matches = box.get_context(bead_spec.BEAD_NAME, 'BEAD3', timestamp)
    assert 'BEAD3' == matches.best.name


def test_box_methods_tolerate_junk_in_box(box_with_junk):
    """Test that box methods work even with junk files present."""
    assert set(['bead1', 'bead2', 'BEAD3']) == set(b.name for b in box_with_junk.all_beads())
