import click

from ._common import common_options
from ._login_and_logout import login, logout
from .assembler import assemble_cli
from .extractor import extract_cli


@click.group("searchable-files")
@common_options
def main():
    pass


main.add_command(login)
main.add_command(logout)
main.add_command(extract_cli)
main.add_command(assemble_cli)
