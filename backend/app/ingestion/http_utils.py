import httpx

from app.ingestion.exceptions import AQIProviderError

REQUEST_TIMEOUT_SECONDS = 5.0


def get_json(provider: str, url: str, params: dict | None = None, headers: dict | None = None) -> dict:
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            response = httpx.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            last_error = exc
    raise AQIProviderError(provider, str(last_error))
