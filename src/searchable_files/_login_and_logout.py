import platform

import click
import globus_sdk

from ._common import (
    AUTH_OPENID_SCOPE,
    AUTH_RESOURCE_SERVER,
    SEARCH_ALL_SCOPE,
    SEARCH_RESOURCE_SERVER,
    internal_auth_client,
    token_storage_adapter,
)


def _check_logged_in():
    adapter = token_storage_adapter()

    search_rt = (
        adapter.read_as_dict().get(SEARCH_RESOURCE_SERVER, {}).get("refresh_token")
    )
    if search_rt is None:
        return False
    native_client = internal_auth_client()
    res = native_client.oauth2_validate_token(search_rt)
    return res["active"]


def _revoke_current_tokens(native_client):
    adapter = token_storage_adapter()
    all_tokendata = adapter.read_as_dict().values()
    for token_data in all_tokendata:
        native_client.oauth2_revoke_token(token_data["access_token"])
        native_client.oauth2_revoke_token(token_data["refresh_token"])


@click.command(
    "login",
    help=(
        "Login to Searchable Files. "
        "Necessary before any 'searchable-files' commands which "
        "require authentication will work"
    ),
)
@click.option(
    "--force", is_flag=True, help="Do a fresh login, ignoring any existing credentials"
)
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
        requested_scopes=[SEARCH_ALL_SCOPE, AUTH_OPENID_SCOPE],
        refresh_tokens=True,
        prefill_named_grant=label,
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
    _revoke_current_tokens(native_client)
    token_storage_adapter().store(tkn)

    click.echo(
        """\

You have successfully logged in to Searchable Files
"""
    )


@click.command(
    "logout",
    help=(
        "Logout of Searchable Files. "
        "Removes your Globus tokens from local storage, "
        "and revokes them so that they cannot be used anymore"
    ),
)
@click.confirmation_option(
    prompt="Are you sure you want to logout?",
    help='Automatically say "yes" to all prompts',
)
def logout():
    native_client = internal_auth_client()
    adapter = token_storage_adapter()

    for rs in (SEARCH_RESOURCE_SERVER, AUTH_RESOURCE_SERVER):
        token_data = adapter.read_as_dict().get(rs, {})
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
                click.echo(
                    "Failed to reach Globus to revoke tokens. "
                    "Because we cannot revoke these tokens, cancelling logout"
                )
                click.get_current_context().exit(1)

    # clear token data from storage
    adapter.remove_tokens_for_resource_server(SEARCH_RESOURCE_SERVER)
    adapter.remove_tokens_for_resource_server(AUTH_RESOURCE_SERVER)

    click.echo(
        """\
You are now successfully logged out of Searchable Files.
You may also want to logout of any browser session you have with Globus:

  https://auth.globus.org/v2/web/logout
"""
    )
