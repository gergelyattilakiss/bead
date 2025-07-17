import io
import os
import stat
import contextlib
import shutil
import tempfile
from pathlib import Path


def ensure_directory(path: Path):
    path_str = path.as_posix() if hasattr(path, 'as_posix') else str(path)
    if not os.path.exists(path_str):
        os.makedirs(path_str)

    assert os.path.isdir(path_str)


def write_file(path: Path, content: bytes | str):
    path_str = path.as_posix() if hasattr(path, 'as_posix') else str(path)
    if isinstance(content, bytes):
        f = open(path_str, 'wb')

        with f:
            f.write(content)
    else:
        f = io.open(path_str, 'wt', encoding='utf-8')

        with f:
            f.write(content)


def read_file(path: Path):
    path_str = path.as_posix() if hasattr(path, 'as_posix') else str(path)
    with io.open(path_str, 'rt', encoding='utf-8') as f:
        return f.read()


@contextlib.contextmanager
def temp_dir(dir=None):
    if dir is None:
        dir = Path.cwd()
    ensure_directory(dir)

    temp_dir = tempfile.mkdtemp(dir=str(dir))
    try:
        yield Path(temp_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def make_readonly(path: Path):
    '''
    WARNING: It does not work for Windows folders.

    Might fail (silently) on other systems as well.
    '''
    path_str = path.as_posix() if hasattr(path, 'as_posix') else str(path)
    mode = os.stat(path_str)[stat.ST_MODE]
    os.chmod(path_str, mode & ~stat.S_IWRITE)


def make_writable(path: Path):
    path_str = path.as_posix() if hasattr(path, 'as_posix') else str(path)
    mode = os.stat(path_str)[stat.ST_MODE]
    os.chmod(path_str, mode | stat.S_IWRITE)


def all_subpaths(dir: Path, followlinks=False):
    dir_str = dir.as_posix() if hasattr(dir, 'as_posix') else str(dir)
    for root, _dirs, files in os.walk(dir_str, followlinks=followlinks):
        root = Path(root)
        yield root
        for file in files:
            yield root / file


def rmtree(root: Path, *args, **kwargs):
    for path in all_subpaths(root, followlinks=False):
        path_str = path.as_posix() if hasattr(path, 'as_posix') else str(path)
        if not os.path.islink(path_str):
            make_writable(path)
    root_str = root.as_posix() if hasattr(root, 'as_posix') else str(root)
    shutil.rmtree(root_str, *args, **kwargs)
