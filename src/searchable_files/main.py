import platform

import click
import globus_sdk

from .assembler import assemble_cli
from .extractor import extract_cli
from .lib import APP_SCOPES, common_options, internal_auth_client, token_storage_adapter
from .manage_index import create_index, show_index
from .query import query_cli
from .submitter import submit_cli
from .watcher import watch_cli


@click.group("searchable-files")
@common_options
def cli():
    pass


# index management
cli.add_command(create_index)
cli.add_command(show_index)
# cli workflow
cli.add_command(extract_cli)
cli.add_command(assemble_cli)
cli.add_command(submit_cli)
cli.add_command(watch_cli)
# query results
cli.add_command(query_cli)


def _check_logged_in():
    adapter = token_storage_adapter()
    native_client = internal_auth_client()

    validity = []
    for token_data in adapter.read_as_dict().values():
        refresh_token = token_data.get("refresh_token")
        response = native_client.oauth2_validate_token(refresh_token)
        validity.append(response["active"])
    return validity != [] and all(validity)


def _revoke_current_tokens(native_client, abort_on_fail=True):
    adapter = token_storage_adapter()
    for rs, token_data in adapter.read_as_dict().items():
        for token_name in ("access_token", "refresh_token"):
            # first lookup the token -- if not found we'll continue
            token = token_data.get(token_name)
            if not token:
                continue

            # token was found, so try to revoke it
            try:
                native_client.oauth2_revoke_token(token)
            # if we network error, revocation failed -- print message and abort so
            # that we can revoke later when the network is working
            except globus_sdk.NetworkError:
                if abort_on_fail:
                    click.echo(
                        "Failed to reach Globus to revoke tokens. "
                        "Because we cannot revoke these tokens, cancelling logout"
                    )
                    click.get_current_context().exit(1)

        # clear token data from storage
        adapter.remove_tokens_for_resource_server(rs)


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
    if not force and _check_logged_in():
        click.echo(
            """\
You are already logged in!

You may force a new login with
  searchable-files login --force
"""
        )
        return

    # get the NativeApp client object
    native_client = internal_auth_client()

    label = platform.node() or None
    native_client.oauth2_start_flow(
        requested_scopes=APP_SCOPES, refresh_tokens=True, prefill_named_grant=label
    )
    linkprompt = "Please log into Globus here"
    click.echo(
        "\n".join(
            [
                linkprompt,
                "-" * len(linkprompt),
                native_client.oauth2_get_authorize_url(),
                "-" * len(linkprompt),
            ]
        )
    )
    auth_code = click.prompt("Enter the resulting Authorization Code here").strip()
    tkn = native_client.oauth2_exchange_code_for_tokens(auth_code)
    _revoke_current_tokens(native_client, abort_on_fail=False)
    token_storage_adapter().store(tkn)

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
    native_client = internal_auth_client()
    _revoke_current_tokens(native_client)
    click.echo(
        """\
You are now successfully logged out of Searchable Files.
You may also want to logout of any browser session you have with Globus:

  https://auth.globus.org/v2/web/logout
"""
    )
