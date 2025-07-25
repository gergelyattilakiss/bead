import os
import pytest

from .test_robot import Robot

from bead.tech.timestamp import timestamp as now_ts
from bead.workspace import Workspace


@pytest.fixture
def box(tmp_path_factory):
    return tmp_path_factory.mktemp("box")


@pytest.fixture
def timestamp():
    return now_ts()


@pytest.fixture
def bead(tmp_path_factory, timestamp):
    tmp = tmp_path_factory.mktemp("bead_tmp")
    ws = Workspace(tmp / 'ws')
    ws.create('a bead kind')
    bead_archive = tmp / 'bead.zip'
    ws.pack(bead_archive, timestamp, comment='bead for a shared box')
    return bead_archive


@pytest.fixture
def alice(box):
    with Robot() as robot:
        robot.cli('box', 'add', 'bobbox', box)
        yield robot


@pytest.fixture
def bob(box):
    with Robot() as robot:
        robot.cli('box', 'add', 'alicebox', box)
        yield robot


def test_shared_box_update(alice, bob, bead):
    bob.cli('new', 'bobbead')
    bob.cd('bobbead')
    bob.cli('input', 'add', 'alicebead1', bead)
    bob.cli('input', 'add', 'alicebead2', bead)

    alice.cli('develop', bead)
    alice.cd('bead')
    alice.write_file('output/datafile', '''Alice's new data''')
    alice.cli('save')

    # update only one input
    bob.cli('input', 'update', 'alicebead1')

    datafile1 = bob.cwd / 'input/alicebead1/datafile'
    assert datafile1.exists()
    assert '''Alice's new data''' in datafile1.read_text()

    # second input directory not changed
    datafile2 = bob.cwd / 'input/alicebead2/datafile'
    assert not datafile2.exists()

    # update all inputs
    bob.cli('input', 'update')

    assert datafile2.exists()
    assert '''Alice's new data''' in datafile2.read_text()


@pytest.fixture
def robot():
    with Robot() as robot_instance:
        yield robot_instance


@pytest.fixture
def dir1(robot):
    os.makedirs(robot.cwd / 'dir1')
    return 'dir1'


@pytest.fixture
def dir2(robot):
    os.makedirs(robot.cwd / 'dir2')
    return 'dir2'


def test_list_when_there_are_no_boxes(robot):
    robot.cli('box', 'list')
    assert 'There are no defined boxes' in robot.stdout


def test_add_non_existing_directory_fails(robot):
    robot.cli('box', 'add', 'notadded', 'non-existing')
    assert 'ERROR' in robot.stdout
    assert 'notadded' not in robot.stdout


def test_add_multiple(robot, dir1, dir2):
    robot.cli('box', 'add', 'name1', 'dir1')
    robot.cli('box', 'add', 'name2', 'dir2')
    assert 'ERROR' not in robot.stdout

    robot.cli('box', 'list')
    assert 'name1' in robot.stdout
    assert 'name2' in robot.stdout
    assert 'dir1' in robot.stdout
    assert 'dir2' in robot.stdout


def test_add_with_same_name_fails(robot, dir1, dir2):
    robot.cli('box', 'add', 'name', 'dir1')
    assert 'ERROR' not in robot.stdout

    robot.cli('box', 'add', 'name', 'dir2')
    assert 'ERROR' in robot.stdout


def test_add_same_directory_twice_fails(robot, dir1):
    robot.cli('box', 'add', 'name1', dir1)
    assert 'ERROR' not in robot.stdout

    robot.cli('box', 'add', 'name2', dir1)
    assert 'ERROR' in robot.stdout


def test_forget_box(robot, dir1, dir2):
    robot.cli('box', 'add', 'box-to-delete', dir1)
    robot.cli('box', 'add', 'another-box', dir2)

    robot.cli('box', 'forget', 'box-to-delete')
    assert 'forgotten' in robot.stdout

    robot.cli('box', 'list')
    assert 'box-to-delete' not in robot.stdout
    assert 'another-box' in robot.stdout


def test_forget_nonexisting_box(robot):
    robot.cli('box', 'forget', 'non-existing')
    assert 'WARNING' in robot.stdout


def test_rewire(robot, dir1):
    # This is a long test, but easy to explain:
    # There are 3 beads a, b, and x stored in a box ('hack-box')
    # a, and b are standalone beads without inputs.
    # While x has 2 inputs: input-a and input-b linking to a and b respectfully.
    # In this configuration the x bead can be developed and the inputs loaded.
    # When a is renamed in the box, a new checkout of bead x can not load a anymore.
    # This situation is fixed with the rewire command[s],
    # and a new checkout of x and loading its inputs is demonstrated
    # as functionality verification.
    def make_bead(name, inputs=()):
        robot.cli('new', name)
        robot.cd(name)
        for input in inputs:
            robot.cli('input', 'add', f'input-{input}', input)
        robot.write_file('output/README', name)
        robot.cli('save')
        robot.cd('..')
        robot.cli('zap', name)

    robot.cli('box', 'add', 'hack-box', dir1)
    make_bead('a')
    make_bead('b')
    make_bead('x', inputs=['a', 'b'])

    # a -> x
    # b -> x

    # rename 'a' to 'renamed'
    for f in (robot.cwd / dir1).glob('a_*.zip'):
        # we need to keep the timestamp and zip extension
        # for the bead to remain discoverable
        ts_zip = os.path.basename(f).split('_')[1]
        os.rename(f, robot.cwd / dir1 / f'renamed_{ts_zip}')
    for f in (robot.cwd / dir1).glob('a*'):
        os.remove(f)

    # "renamed" ~> x
    # b -> x

    # test of test setup: 'input load' should fail due to the renamed input a
    robot.cli('develop x')
    robot.cd('x')
    robot.cli('input load')
    assert 'WARNING' in robot.stderr
    assert not os.path.exists(robot.cwd / 'input/input-a')
    assert 'b' == robot.read_file('input/input-b/README')
    robot.cd('..')
    robot.cli('zap x')
    # end of test setup

    # test: fix input loading by modifying the input-map with rewire commands
    robot.cli('web rewire-options rewire.json')
    robot.cli('box rewire hack-box rewire.json')

    # "renamed" -> x
    # b -> x

    # verify, that the renamed bead is loaded (input map fixed up)
    robot.cli('develop x')
    robot.cd('x')
    robot.cli('input load')
    assert robot.stderr == ''
    assert 'a' == robot.read_file('input/input-a/README')
    assert 'b' == robot.read_file('input/input-b/README')
