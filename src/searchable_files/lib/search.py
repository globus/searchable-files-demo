import globus_sdk

from .auth import internal_auth_client, token_storage_adapter

SEARCH_RESOURCE_SERVER = "search.api.globus.org"


def search_client():
    storage_adapter = token_storage_adapter()
    maybe_existing = storage_adapter.read_as_dict()

    refresh_token, access_token, access_token_expires = None, None, None
    if maybe_existing is not None and SEARCH_RESOURCE_SERVER in maybe_existing:
        searchdata = maybe_existing[SEARCH_RESOURCE_SERVER]
        access_token = searchdata["access_token"]
        refresh_token = searchdata["refresh_token"]
        access_token_expires = searchdata["expires_at_seconds"]

    authorizer = None
    if access_token_expires is not None:
        authorizer = globus_sdk.RefreshTokenAuthorizer(
            refresh_token,
            internal_auth_client(),
            access_token,
            int(access_token_expires),
            on_refresh=storage_adapter.on_refresh,
        )

    return globus_sdk.SearchClient(authorizer=authorizer, app_name="searchable-files")
