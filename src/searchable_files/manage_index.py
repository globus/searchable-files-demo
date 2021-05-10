import click

from .lib import (
    auth_client,
    common_options,
    prettyprint_json,
    search_client,
    token_storage_adapter,
)


@click.command(
    "create-index",
    help="Create the Index for Searchable Files.\n"
    "The index will be owned by the current user and will have an "
    "automatically chosen name and description.",
)
@common_options
def create_index():
    adapter = token_storage_adapter()
    client = search_client()

    userinfo = auth_client().oauth2_userinfo()
    username = userinfo["preferred_username"]
    res = client.post(
        "/beta/index",
        {
            "display_name": "Searchable Files Demo Index",
            "description": "An index created for use with the Searchable Files Demo App. "
            f"Created by {username}",
        },
    )
    index_id = res["id"]

    adapter.store_config("index_info", {"index_id": index_id})

    click.echo(f"successfully created index, id='{index_id}'")


@click.command(
    "show-index",
    help="Show index info.\n"
    "Detailed info about the Searchable Files index. "
    "Must run after create-index.\n"
    "The data is verbatim output from the Globus Search API.",
)
@common_options
def show_index():
    adapter = token_storage_adapter()
    client = search_client()

    index_info = adapter.read_config("index_info")
    if not index_info:
        raise click.UsageError("You must create an index with `create-index` first!")
    index_id = index_info["index_id"]

    res = client.get(f"/v1/index/{index_id}")
    click.echo(prettyprint_json(res.data))


@click.command(
    "set-index",
    help="Set the Index for Searchable Files.\n"
    "If an index has already been created, either via a previous use of "
    "`create-index` or by another means, this command allows you to set the "
    "default index for commands like `submit` and `query`.",
)
@common_options
@click.argument("INDEX_ID", type=click.UUID)
def set_index(index_id):
    adapter = token_storage_adapter()
    adapter.store_config("index_info", {"index_id": str(index_id)})
    click.echo(f"successfully updated configured index, id='{index_id}'")


def add_commands(group):
    group.add_command(create_index)
    group.add_command(show_index)
    group.add_command(set_index)
