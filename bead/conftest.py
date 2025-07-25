import contextlib
import io
import os
import pathlib
import tempfile
import pytest

from . import tech


@contextlib.contextmanager
def chdir(directory):
    cwd = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(cwd)


@contextlib.contextmanager
def setenv(variable: str, value: str):
    old_value = os.environ.get(variable)
    try:
        os.environ[variable] = value
        yield
    finally:
        if old_value is None:
            del os.environ[variable]
        else:
            os.environ[variable] = old_value


class Fixture:
    def __init__(self):
        self.__cleanups = []

    def setUp(self):
        pass

    def cleanUp(self):
        while self.__cleanups:
            cleanup, args, kwargs = self.__cleanups[-1]
            cleanup(*args, **kwargs)
            del self.__cleanups[-1]

    def addCleanup(self, cleanup, *args, **kwargs):
        self.__cleanups.append((cleanup, args, kwargs))

    def useFixture(self, fixture):
        fixture.setUp()
        self.addCleanup(fixture.cleanUp)
        return fixture

    def __enter__(self):
        self.setUp()
        return self

    def __exit__(self, *_exc):
        self.cleanUp()


class TempDir(Fixture):
    path: tech.fs.Path

    def setUp(self):
        super().setUp()
        self.path = tech.fs.Path(tempfile.mkdtemp())
        # we need our own rmtree, that can remove read only files as well
        self.addCleanup(tech.fs.rmtree, self.path, ignore_errors=True)


class _CaptureStream(Fixture):

    def __init__(self, redirector):
        self.redirector = redirector
        self.string_stream = io.StringIO()
        super().__init__()

    def setUp(self):
        super().setUp()
        redirect = self.redirector(self.string_stream)
        redirect.__enter__()
        self.addCleanup(lambda: redirect.__exit__(None, None, None))

    @property
    def text(self):
        return self.string_stream.getvalue()


def CaptureStdout():
    return _CaptureStream(contextlib.redirect_stdout)


def CaptureStderr():
    return _CaptureStream(contextlib.redirect_stderr)


class CheckAssertions:
    """Helper class providing assertion methods for tests."""
    
    def file_contains(self, filename, content_fragment):
        assert content_fragment in pathlib.Path(filename).read_text()

    def file_exists(self, filename):
        assert os.path.exists(filename)

    def file_does_not_exists(self, filename):
        assert not os.path.exists(filename)


@pytest.fixture
def temp_dir():
    """Provide a temporary directory that gets cleaned up after the test."""
    with TempDir() as td:
        yield td.path


@pytest.fixture
def capture_stdout():
    """Capture stdout during test execution."""
    with CaptureStdout() as capture:
        yield capture


@pytest.fixture
def capture_stderr():
    """Capture stderr during test execution."""
    with CaptureStderr() as capture:
        yield capture


@pytest.fixture
def check():
    """Provide assertion helper methods."""
    return CheckAssertions()
