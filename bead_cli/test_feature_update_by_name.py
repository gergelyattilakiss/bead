import os
import shutil
from typing import Dict

from bead.archive import Archive
from . import test_fixtures as fixtures


def test_basic_support(robot, bead_a, bead_with_history, box, check):
    """
    update by name not by kind
    """
    # (bead_with_history has 5 beads sharing the same name, kind)

    cd = robot.cd
    cli = robot.cli
    bead1 = 'bead1'
    bead2 = 'bead2'
    bead3 = 'bead3'

    def copy(timestamp, new_name):
        _copy(box, bead_with_history, timestamp, new_name)

    # verify, that `add`, `save`, `develop`, `update`, and `status` all work with input_map

    copy(fixtures.TS1, bead1)
    copy(fixtures.TS2, bead2)

    # setup - bead_a with 2 inputs
    cli('develop', bead_a)
    cd(bead_a)
    cli('input', 'add', 'input1', bead1)
    cli('input', 'add', 'input2', bead2)
    check.loaded('input1', fixtures.TS1)
    check.loaded('input2', fixtures.TS2)

    cli('status')
    assert bead1 in robot.stdout
    assert bead2 in robot.stdout

    # `update` works by name, not by kind
    copy(fixtures.TS3, bead1)
    cli('input', 'update')
    check.loaded('input1', fixtures.TS3)
    check.loaded('input2', fixtures.TS2)

    # save & develop works with names
    cli('save')
    cd('..')
    cli('zap', bead_a)
    cli('develop', bead_a)
    cd(bead_a)
    copy(fixtures.TS4, bead1)
    copy(fixtures.TS3, bead2)
    cli('input', 'update')
    check.loaded('input1', fixtures.TS4)
    check.loaded('input2', fixtures.TS3)

    # `update` also sets the bead name for input
    copy(fixtures.TS1, bead3)
    cli('input', 'update', 'input2', bead3)
    check.loaded('input2', fixtures.TS1)
    copy(fixtures.TS4, bead3)
    cli('input', 'update', 'input2')
    check.loaded('input1', fixtures.TS4)
    check.loaded('input2', fixtures.TS4)


def test_load_finds_renamed_bead_only_after_rewiring_input_map(
    robot, bead_a, bead_b, box, beads: Dict[str, Archive], check
):
    # reason: speed
    # reason: implementation simplicity
    cd = robot.cd
    cli = robot.cli

    # develop new version of A using B as its input
    cli('develop', bead_a)
    cd(bead_a)
    cli('input', 'add', 'b', bead_b)
    check.loaded('b', bead_b)

    # rename B to C
    os.rename(beads[bead_b].archive_filename, box.directory / f'c_{fixtures.TS1}.zip')

    # unload input
    cli('input', 'unload', 'b')

    # try to load input again
    cli('input', 'load', 'b')
    check.not_loaded('b')

    cli('input', 'map', 'b', 'c')
    print(robot.stderr)
    cli('input', 'load', 'b')
    check.loaded('b', bead_b)


def _copy(box, bead_name, bead_freeze_time, new_name):
    """
    Copy a bead to a new name within box.
    """
    # FIXME: this test helper uses private to box implementation information
    # namely how the current box implementation stores archives in zip files
    source = box.directory / f'{bead_name}_{bead_freeze_time}.zip'
    destination = box.directory / f'{new_name}_{bead_freeze_time}.zip'
    shutil.copy(source, destination)
