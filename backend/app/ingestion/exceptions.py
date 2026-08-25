class AQIProviderError(Exception):
    def __init__(self, provider: str, detail: str) -> None:
        self.provider = provider
        self.detail = detail
        super().__init__(f"{provider}: {detail}")


class ProviderNotConfiguredError(AQIProviderError):
    def __init__(self, provider: str) -> None:
        super().__init__(provider, "no API credential configured")
