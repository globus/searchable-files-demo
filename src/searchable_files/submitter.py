import json
import os

import click

from ._common import all_filenames, common_options, search_client, token_storage_adapter


def submit_doc(client, index_id, filename, task_list_file):
    with open(filename) as fp:
        data = json.load(fp)
    res = client.ingest(index_id, data)
    with open(task_list_file, "a") as fp:
        fp.write(res["task_id"] + "\n")


@click.command("submit")
@click.option(
    "--directory",
    default="output/assembled",
    show_default=True,
    help="A path, relative to the current working directory, "
    "containing ingest documents to submit",
)
@click.option(
    "--output",
    default="output/task_submit",
    show_default=True,
    help="A directory relative to the current working directory, "
    "where the resulting task IDs be written",
)
@click.option(
    "--index-id",
    default=None,
    help="Override the index ID where the tasks should be submitted. "
    "If omitted, the index created with `create-index` will be used.",
)
@common_options
def submit_cli(directory, output, index_id):
    client = search_client()

    os.makedirs(output, exist_ok=True)
    task_list_file = os.path.join(output, "tasks.txt")
    with open(task_list_file, "w"):  # empty the file (open in write mode)
        pass

    if not index_id:
        index_info = token_storage_adapter().read_config("index_info")
        if index_info is None:
            raise click.UsageError(
                "Cannot submit without first setting up "
                "an index or passing '--index-id'"
            )
        index_id = index_info["index_id"]

    for filename in all_filenames(directory):
        submit_doc(client, index_id, filename, task_list_file)

    click.echo(
        f"""\
ingest document submission (task submission) complete
task IDs are visible in
    {task_list_file}"""
    )
