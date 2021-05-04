import os

import click


def common_options(f):
    # any shared/common options for all commands
    return click.help_option("-h", "--help")(f)


def all_filenames(directory):
    for dirpath, _dirnames, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.join(dirpath, f)
