from backend.auth.providers.base import OauthProvider
from backend.auth.providers.microsoft import MicrosoftOauthProvider

providers = {}


def get_oauth_provider(name: str) -> OauthProvider:
    if name in providers:
        return providers[name]
    raise ValueError(f"Oauth provider {name} was not found")


def register_provider(name: str, instance: OauthProvider):
    if name in providers:
        raise ValueError(f"Oauth provider {name} is already registered")
    providers[name] = instance
    print(f"New oauth provider {name} was registered")


register_provider("microsoft", MicrosoftOauthProvider())
