import os

import click

from .auth import auth_client, internal_auth_client, token_storage_adapter
from .search import search_client

APP_SCOPES = ["openid", "profile", "urn:globus:auth:scope:search.api.globus.org:all"]


def common_options(f):
    # any shared/common options for all commands
    return click.help_option("-h", "--help")(f)


def all_filenames(directory):
    for dirpath, _dirnames, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.relpath(os.path.join(dirpath, f))


__all__ = (
    "APP_SCOPES",
    "common_options",
    "all_filenames",
    "token_storage_adapter",
    "internal_auth_client",
    "auth_client",
    "search_client",
)