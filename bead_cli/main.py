# PYTHON_ARGCOMPLETE_OK
import os
import subprocess
import sys
import textwrap
import traceback
import importlib.metadata

from collections.abc import Sequence

import appdirs
from .cmdparse import Parser, Command

from bead.tech.fs import Path
from bead.tech.timestamp import timestamp
from .common import warning
from . import workspace
from . import input
from . import box
from .web import commands as web


def output_of(shell_cmd: str):
    return subprocess.check_output(shell_cmd, shell=True).decode('utf-8').strip()


class _git:
    def __init__(self):
        try:
            from . import git_info
            self.repo = git_info.GIT_REPO
            self.branch = git_info.GIT_BRANCH
            self.date = git_info.GIT_DATE
            self.commit = git_info.GIT_HASH
            self.tag = git_info.TAG_VERSION
            self.dirty = git_info.DIRTY
        except ImportError:
            # No git_info means this is likely an installed package, not a dev build
            # Only try git commands if we're actually in a git repo
            try:
                self.repo = output_of('git config --get remote.origin.url')
                self.branch = output_of('git branch --show-current')
                self.date = output_of("git show HEAD --pretty=tformat:'%cI' --no-patch")
                self.commit = output_of("git show HEAD --pretty=tformat:'%H' --no-patch")
                self.tag = output_of('git describe --tags')
                modified_files = [
                    line for line in output_of('git status --porcelain=1').splitlines()
                    if not line.startswith('??') and ' bead_cli/git_info.py' not in line]
                self.dirty = modified_files != []
            except:
                # Not in a git repo or git not available - this is a normal install
                self.repo = ''
                self.branch = ''
                self.date = ''
                self.commit = ''
                self.tag = ''
                self.dirty = False  # Installed packages are never "dirty"

        self.version_info = textwrap.dedent(
            '''
            Python:
            ------
            {sys.version}

            Bead source:
            -----------
            origin:  {self.repo}
            branch:  {self.branch}
            date:    {self.date}
            hash:    {self.commit}
            version: {self.tag}{version_suffix}
            '''
        ).format(self=self, sys=sys, version_suffix='-dirty' if self.dirty else '')


git = _git()


class CmdVersion(Command):
    '''
    Show program version info
    '''

    def run(self, args):
        try:
            version = importlib.metadata.version('bead')
            print(f'bead version {version}')
        except importlib.metadata.PackageNotFoundError:
            # Development mode - show git info
            print('bead development version')
            print(git.version_info)
        
        # Always show Python version
        print(f'\nPython {sys.version}')


def make_argument_parser(defaults):
    parser = Parser.new(defaults)
    (parser
        .commands(
            ('new', workspace.CmdNew, 'Create and initialize new workspace directory with a new bead.'),
            ('develop', workspace.CmdDevelop, 'Create workspace from specified bead.'),
            ('save', workspace.CmdSave, 'Save workspace in a box.'),
            ('status', workspace.CmdStatus, 'Show workspace information.'),
            ('web', web.CmdWeb, 'Manage/visualize the big picture - connections between beads.'),
            ('zap', workspace.CmdZap, 'Delete workspace.'),
            ('xmeta', box.CmdXmeta, 'eXport eXtended meta attributes to a file next to zip archive.'),
            ('version', CmdVersion, 'Show program version.'),
        ))

    (parser
        .group('input', 'Manage data loaded from other beads')
        .commands(
            ('add', input.CmdAdd, 'Define dependency and load its data.'),
            ('delete', input.CmdDelete, 'Forget all about an input.'),
            ('rm', input.CmdDelete, 'Forget all about an input. (alias for delete)'),
            ('map', input.CmdMap, 'Change the name of the bead from which the input is loaded/updated.'),
            ('update', input.CmdUpdate, 'Update input[s] to newest version or defined bead.'),
            ('load', input.CmdLoad, 'Load data from already defined dependency.'),
            ('unload', input.CmdUnload, 'Unload input data.'),
        ))

    (parser
        .group('box', 'Manage bead boxes')
        .commands(
            ('add', box.CmdAdd, 'Define a box.'),
            ('list', box.CmdList, 'Show known boxes.'),
            ('forget', box.CmdForget, 'Forget a known box.'),
            ('rewire', box.CmdRewire, 'Remap inputs.'),
        ))

    parser.autocomplete()

    return parser


def run(config_dir: str, argv: Sequence[str]):
    parser_defaults = dict(config_dir=Path(config_dir))
    parser = make_argument_parser(parser_defaults)
    return parser.dispatch(argv)


FAILURE_TEMPLATE = """\
{exception}

An unexpected error occurred. Please report this issue at:
{repo}/issues/new

Include the full error report from: {error_report}

Note: The console output above has been shortened. 
Please use the full error report file when creating the issue.
"""


def main(run=run):
    if git.dirty:
        warning('test build, DO NOT USE for production!!!')
    config_dir = appdirs.user_config_dir(
        'bead_cli-6a4d9d98-8e64-4a2a-b6c2-8a753ea61daf')
    try:
        retval = run(config_dir, sys.argv[1:])
    except KeyboardInterrupt:
        print("Interrupted :(", file=sys.stderr)
        retval = -1
    except SystemExit:
        raise
    except BaseException:
        # all remaining errors are catched - including RunTimeErrors
        sys_argv = f'{sys.argv!r}'
        exception = traceback.format_exc()
        short_exception = traceback.format_exc(limit=1)
        error_report = os.path.realpath(f'error_{timestamp()}.txt')
        with open(error_report, 'w') as f:
            f.write(f'sys_argv = {sys_argv}\n')
            f.write(f'{exception}\n')
            f.write(f'{git.version_info}\n')
            if git.dirty:
                f.write('WARNING: TEST BUILD, UNKNOWN, UNCOMMITTED CHANGES !!!\n')
        # Try to get repository URL from package metadata
        try:
            metadata = importlib.metadata.metadata('bead')
            repo_url = metadata.get('Home-page', 'https://github.com/codedthinking/bead')
            if not repo_url:
                # Try project urls
                for key in ['Repository', 'Homepage']:
                    repo_url = metadata.get(f'Project-URL: {key}', '')
                    if repo_url:
                        break
                if not repo_url:
                    repo_url = 'https://github.com/codedthinking/bead'
        except:
            repo_url = 'https://github.com/codedthinking/bead'
        
        print(
            FAILURE_TEMPLATE.format(
                exception=short_exception,
                error_report=error_report,
                repo=repo_url,
            ),
            file=sys.stderr
        )
        retval = -1
    sys.exit(retval)


if __name__ == '__main__':
    main()
