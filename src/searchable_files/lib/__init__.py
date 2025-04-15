import json
import os

import click

from .clients import APP, AUTH_CLIENT, SEARCH_CLIENT


def common_options(f):
    # any shared/common options for all commands
    return click.help_option("-h", "--help")(f)


def all_filenames(directory):
    for dirpath, _dirnames, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.relpath(os.path.join(dirpath, f))


def prettyprint_json(obj, fp=None):
    if fp:
        return json.dump(obj, fp, indent=2, separators=(",", ": "), ensure_ascii=False)
    return json.dumps(obj, indent=2, separators=(",", ": "), ensure_ascii=False)


__all__ = (
    "common_options",
    "all_filenames",
    "prettyprint_json",
    "APP",
    "AUTH_CLIENT",
    "SEARCH_CLIENT",
)
