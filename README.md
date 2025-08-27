    B-E-+
     \ \ \
      +-A-D

# BEAD


BEAD is a format for freezing and storing computations while `bead` is a tool that helps
capturing and managing computations in BEAD formats.


## Concept

Given a discrete computation of the form

    output = function(*inputs)

a BEAD captures all three named parts:

- `output` - *data files* (results of the computation)
- `function` - *source code files*, that when run hopefully compute `output` from `inputs`
- `inputs` - are other BEADs' `output` and thus stored as *references to* those *BEADs*

As a special case pure data can be thought of as *constant computation*
having only output but neither inputs nor source code.

A BEAD has some other metadata - notably it has a `kind` property which is shared by
different versions of the conceptually same computation (input or function may be updated/improved)
and a timestamp when the computation was frozen.

The `kind` and timestamp properties enable a meaningful `update` operation on inputs.

New computations get a new, universally unique `kind` (technically an uuid).


## Status

### Used in production for 2 years now, there are 100+ frozen computations

Although most of the important stuff is implemented, there are still some raw edges.

Documentation for the tool is mostly the command line help.

The `doc` directory has concept descriptions, maybe some use cases,
but there are also design fragments - you might be mislead by them as they
are nor describing the current situations nor are they showing the future.
FIXME: clean up documentation.


## Installation

### Using pipx (recommended)

The easiest way to install `bead` is using [pipx](https://pypa.github.io/pipx/), which installs Python applications in isolated environments:

#### From GitHub (latest development version)
```bash
pipx install git+https://github.com/codedthinking/bead.git
```

#### From a specific branch or tag
```bash
# Install from a branch
pipx install git+https://github.com/codedthinking/bead.git@branch-name

# Install from a tag
pipx install git+https://github.com/codedthinking/bead.git@v0.8.1
```

#### Upgrade to latest version
```bash
pipx upgrade bead
```

#### From PyPI (coming soon)
Once published to PyPI, you'll be able to install with:
```bash
pipx install bead
```

### Using pip

You can also install using pip, though pipx is recommended for better isolation:

```bash
pip install git+https://github.com/codedthinking/bead.git
```

### Building from source

Ensure you have Python 3.10+ installed.

Run `make executables` to create standalone executables:

```
$ make executables
```

This generates one-file executables for unix, mac, and windows in the `executables` directory:
- `bead` unix & mac
- `bead.cmd` windows

Move/copy the `bead` binary for your platform to some directory on your `PATH`.

E.g.

```
$ cp executables/bead ~/.local/bin
```

If you test it, please give [feedback](../../issues) on
- general usability
- misleading/unclear help (currently: command line help)
- what is missing (I know about documentation)
- what is not working as you would expect

Any other nuisance reported - however minor you think it be - is important and welcome!

Thank you for your interest!


## TODOs

- FIXME: test helper uses private to box implementation information (test_feature_update_by_name.py)
- TODO: log/report problem (box.py)
- XXX: (usability) save - support saving directly to a directory outside of workspace
- XXX: try to load smaller inputs?
