from backend.auth.providers.base import OauthProvider
from backend.auth.providers.microsoft import MicrosoftOauthProvider

providers = {
    "microsoft": MicrosoftOauthProvider(),
}


def get_oauth_provider(name: str) -> OauthProvider:
    if name in providers:
        return providers[name]
    raise ValueError(f"Oauth provider {name} was not found")
