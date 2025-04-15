import json
import os

import click

from .lib import SEARCH_CLIENT, all_filenames, common_options


def submit_doc(index_id, filename, task_list_file):
    with open(filename) as fp:
        data = json.load(fp)
    res = SEARCH_CLIENT.ingest(index_id, data)
    with open(task_list_file, "a") as fp:
        fp.write(res["task_id"] + "\n")


@click.command(
    "submit",
    help=(
        "Submit Ingest documents as new Tasks.\n"
        "Reading Ingest documents produced by the Assembler, submit them "
        "each as a new Task and log their task IDs. "
        "These tasks can then be monitored with the `watch` command."
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
@click.option(
    "--directory",
    default="output/assembled",
    show_default=True,
    help=(
        "A path, relative to the current working directory, "
        "containing ingest documents to submit"
    ),
)
@click.option(
    "--output",
    default="output/task_submit",
    show_default=True,
    help=(
        "A directory relative to the current working directory, "
        "where the resulting task IDs be written"
    ),
)
@click.option(
    "--index-id",
    default=None,
    help=(
        "Override the index ID where the tasks should be submitted. "
        "If omitted, the index created with `create-index` will be used."
    ),
)
@common_options
def submit_cli(index_info_file, directory, output, index_id):
    os.makedirs(output, exist_ok=True)
    task_list_file = os.path.join(output, "tasks.txt")
    with open(task_list_file, "w"):  # empty the file (open in write mode)
        pass

    if not index_id:
        try:
            with open(index_info_file, "rb") as fp:
                index_info = json.load(fp)
        except FileNotFoundError as e:
            raise click.UsageError(
                "Cannot submit without first setting up "
                "an index or passing '--index-id'"
            ) from e
        index_id = index_info["index_id"]

    for filename in all_filenames(directory):
        submit_doc(index_id, filename, task_list_file)

    click.echo(
        f"""\
ingest document submission (task submission) complete
task IDs are visible in
    {task_list_file}"""
    )
