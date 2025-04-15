import json

import click

from .lib import (
    AUTH_CLIENT,
    SEARCH_CLIENT,
    common_options,
    prettyprint_json,
)


@click.command(
    "create-index",
    help=(
        "Create the Index for Searchable Files.\n"
        "The index will be owned by the current user and will have an "
        "automatically chosen name and description."
    ),
)
@click.option(
    "--index-info-file",
    default="data/index_info.json",
    show_default=True,
    help=(
        "A path, relative to the current working directory, "
        "containing where the index information will be stored"
    ),
)
@common_options
def create_index(index_info_file):
    userinfo = AUTH_CLIENT.oauth2_userinfo()
    username = userinfo["preferred_username"]
    res = SEARCH_CLIENT.create_index(
        "Searchable Files Demo Index",
        (
            "An index created for use with the Searchable Files Demo App. "
            f"Created by {username}"
        ),
    )
    index_id = res["id"]

    with open(index_info_file, "w") as fp:
        json.dump({"index_id": index_id}, fp)

    click.echo(f"successfully created index, id='{index_id}'")


@click.command(
    "show-index",
    help=(
        "Show index info.\n"
        "Detailed info about the Searchable Files index. "
        "Must run after create-index.\n"
        "The data is verbatim output from the Globus Search API."
    ),
)
@click.option(
    "--index-info-file",
    default="data/index_info.json",
    show_default=True,
    help=(
        "A path, relative to the current working directory, "
        "containing where the index information is stored"
    ),
)
@common_options
def show_index(index_info_file):
    try:
        with open(index_info_file, "rb") as fp:
            index_info = json.load(fp)
    except FileNotFoundError as e:
        raise click.UsageError(
            "You must create an index with `create-index` first!"
        ) from e

    index_id = index_info["index_id"]

    res = SEARCH_CLIENT.get_index(index_id)
    click.echo(prettyprint_json(res.data))


@click.command(
    "set-index",
    help=(
        "Set the Index for Searchable Files.\n"
        "If an index has already been created, either via a previous use of "
        "`create-index` or by another means, this command allows you to set the "
        "default index for commands like `submit` and `query`."
    ),
)
@click.option(
    "--index-info-file",
    default="data/index_info.json",
    show_default=True,
    help=(
        "A path, relative to the current working directory, "
        "containing where the index information will be stored"
    ),
)
@common_options
@click.argument("INDEX_ID", type=click.UUID)
def set_index(index_id, index_info_file):
    with open(index_info_file, "w") as fp:
        json.dump({"index_id": str(index_id)}, fp)
    click.echo(f"successfully updated configured index, id='{index_id}'")


def add_commands(group):
    group.add_command(create_index)
    group.add_command(show_index)
    group.add_command(set_index)
