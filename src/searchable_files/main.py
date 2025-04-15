import click

from . import assembler, extractor, manage_index, query, submitter, watcher
from .lib import APP, common_options


@click.group("searchable-files")
@common_options
def cli():
    pass


# index management
manage_index.add_commands(cli)
# cli workflow
cli.add_command(extractor.extract_cli)
cli.add_command(assembler.assemble_cli)
cli.add_command(submitter.submit_cli)
cli.add_command(watcher.watch_cli)
# query results
cli.add_command(query.query_cli)


@cli.command(
    "login",
    help=(
        "Log in to Searchable Files. "
        "Necessary before any 'searchable-files' commands which "
        "require authentication will work"
    ),
)
@click.option(
    "--force", is_flag=True, help="Do a fresh login, ignoring any existing credentials"
)
@common_options
def login(force):
    # if not forcing, stop if user already logged in
    if not force and not APP.login_required():
        click.echo(
            """\
You are already logged in!

You may force a new login with
  searchable-files login --force
"""
        )
        return

    APP.login()

    click.echo(
        """\

You have successfully logged in to Searchable Files
"""
    )


@cli.command(
    "logout",
    help=(
        "Log out of Searchable Files. "
        "Removes your Globus tokens from local storage, "
        "and revokes them so that they cannot be used anymore"
    ),
)
@click.confirmation_option(
    prompt="Are you sure you want to logout?",
    help='Automatically say "yes" to all prompts',
)
@common_options
def logout():
    APP.logout()
    click.echo(
        """\
You are now successfully logged out of Searchable Files.
You may also want to logout of any browser session you have with Globus:

  https://auth.globus.org/v2/web/logout
"""
    )
