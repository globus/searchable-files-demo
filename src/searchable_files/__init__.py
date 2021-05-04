import click

from ._common import common_options
from ._login_and_logout import login, logout
from ._manage_index import create_index, show_index
from .assembler import assemble_cli
from .extractor import extract_cli
from .submitter import submit_cli
from .watcher import watch_cli


@click.group("searchable-files")
@common_options
def main():
    pass


# login/logout
main.add_command(login)
main.add_command(logout)
# index management
main.add_command(create_index)
main.add_command(show_index)
# main workflow
main.add_command(extract_cli)
main.add_command(assemble_cli)
main.add_command(submit_cli)
main.add_command(watch_cli)
