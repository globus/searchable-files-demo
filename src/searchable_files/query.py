import json

import click
import globus_sdk

from .lib import common_options, search_client, token_storage_adapter


@click.command(
    "query",
    help="Perform a search query.\n"
    "This will automatically query the index created with create-index. "
    "This command supports various operations which are specific to the data "
    "generated by searchable-files, but the entire implementation is based  "
    "on standard features of the Globus Search service.\n"
    "You can use a query of '*' to match all data.",
)
@common_options
@click.argument("QUERY_STRING")
@click.option(
    "--limit", type=int, help="Limit the number of results to return", default=5
)
@click.option("--offset", type=int, help="Starting offset for paging", default=0)
@click.option(
    "--advanced",
    is_flag=True,
    help="Perform the search using the advanced query syntax",
)
@click.option(
    "--types",
    help="Filter results to files matching ALL of the listed types (comma-delimited). "
    "For example, '--types=text,non-executable'",
)
@click.option(
    "--types-or",
    help="Filter results to files matching ANY of the listed types (comma-delimited). "
    "For example, '--types=text,binary'",
)
@click.option(
    "--extensions",
    help="Filter results to files with specific extensions. For example "
    "'--extension=txt,png'",
)
@click.option(
    "--no-auth",
    is_flag=True,
    help="Make the query unauthenticated. This will hide any results or entries "
    "in results which you are only able to see because you are listed in their "
    "visible_to permissions.",
)
@click.option(
    "--dump-query",
    help="Write the query structure to a file instead of submitting it to the service",
)
def query_cli(
    query_string,
    limit,
    offset,
    advanced,
    types,
    types_or,
    extensions,
    no_auth,
    dump_query,
):
    adapter = token_storage_adapter()
    client = search_client(authenticated=not no_auth)
    index_info = adapter.read_config("index_info")
    if not index_info:
        raise click.UsageError("You must create an index with `create-index` first!")
    index_id = index_info["index_id"]

    query_obj = globus_sdk.SearchQuery(
        q=query_string, limit=limit, offset=offset, advanced=advanced
    )
    if types:
        query_obj.add_filter("tags", types.split(","))
    if types_or:
        query_obj.add_filter("tags", types_or.split(","), type="match_any")
    if extensions:  # since files can only have one extension, "match_any"
        query_obj.add_filter("extension", extensions.split(","), type="match_any")

    if dump_query:
        with open(dump_query, "w") as fp:
            json.dump(query_obj, fp)
        click.echo("query dumped successfully")
    else:
        click.echo(
            json.dumps(
                client.post_search(index_id, query_obj).data,
                indent=2,
                separators=(",", ": "),
            )
        )