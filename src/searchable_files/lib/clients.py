import globus_sdk

CLIENT_ID = "c1bd6f26-7d46-4ccf-a7af-ddc7dfec2bfe"
APP_CONFIG = globus_sdk.GlobusAppConfig(login_flow_manager="local-server")
APP = globus_sdk.UserApp("searchable-files", client_id=CLIENT_ID, config=APP_CONFIG)


AUTH_CLIENT = globus_sdk.AuthClient(
    app=APP, app_scopes=globus_sdk.Scope.parse("openid profile")
)


SEARCH_CLIENT = globus_sdk.SearchClient(
    app=APP, app_scopes=[globus_sdk.Scope(globus_sdk.SearchClient.scopes.all)]
)
